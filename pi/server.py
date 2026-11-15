#!/usr/bin/env python3
"""The orrery's brain with a touchscreen: a small web server that owns the servos.

The Pi's screen shows ui/index.html full screen (Chromium kiosk). Every tap is
sent here, and the page redraws from /api/state several times a second, so the
screen and a phone browser drive the same model. (A physical KY-040 knob was
planned; dropped 26 Sep 2026: the touchscreen does everything.)

    python3 server.py                 # servos on USB, http://<pi>:8080
    python3 server.py --dry-run       # no servos (try the screen on a laptop)

Admin page (not on the touchscreen): http://<pi>:8080/admin - live servo readings,
the tuning settings (saved to ~/.orrery_settings.json), recent taps.

Tabs (RUN decided 25 Sep 2026; PLANETS replaced GO TO DATE on 26 Sep; TIME TRAVEL,
SCALE and the HEALTH icon 26 Sep; 7 Nov 2026 the old RUN screen went, the SOLAR SYSTEM
view became RUN, and typing a date moved to TIME TRAVEL):
  RUN         the Sun and all nine planets in 3D where the orrery puts them (ui/planets.js),
              the date, Run/Pause, and a  -  N yr/min  +  speed control (the same STEPS
              as the admin page's Slower/Faster: 1, 2, 5, 10, 20, 50, 100; capped at 100
              since 7 Nov 2026 to spare the gears). Tap a planet to open its PLANETS page.
              While running every planet goes round at a steady speed (a circular orbit -
              quieter than Mercury's real speed-up near the Sun), starting from its true
              position. A planet too fast for its servo ("racing") spins at its cap_rpm(b):
              CAP_RPM for Mercury, RACE_STEP_PCT % less per planet out, so the order holds.
              On pause every arm settles on the exact true position for the date.
  PLANETS     a page about the Sun and each planet (facts + a 3D globe you can turn and
              pinch to zoom, ui/planets.js); opens on Saturn. The orrery keeps running.
  TIME TRAVEL four moments in history (EVENTS): tap one and the arms go to that day
              (JPL's Table 2 outside 1800-2100). Under them "Pick a date": the day, month
              and year (1 AD-3000 AD) each set with up/down, then GO. Picking a date while
              running pauses first.
  GALAXY      where the solar system is in the Milky Way (14 Nov 2026): the galaxy in 3D
              with "You are here" at the Sun (ui/planets.js). The orrery keeps running.
  SCALE       the Sun and planets at their true relative sizes, and their distances.
  SETTINGS    (gear icon; "health" in the code) the Pi's temperature and CPU, each
              servo's readings, and the MANUAL / AUTO switch (8 Nov 2026). The server
              starts in AUTO (since 7 Nov 2026, the model built and tested): the arms go
              to the saved date at start-up. In MANUAL the servos are left limp, the date
              logic does not drive them (the screen still animates), and in manual, tap planets in the servo list and set a speed (rpm) to spin just
              those; STOP ramps them down and leaves them limp again. AUTO hands the
              servos back to the date (they first settle on it).
              TRAVEL MODE (AUTO; 8 Nov 2026 as LINE UP, the user's design; renamed and
              turned round 13 Nov 2026; "lineup" / lined_up in the code): every arm points
              away from the screen (orrery.HOME_LON), the planets in one row: for carrying
              the model, for clamping the arms on, and to check the calibration. It stays
              through a restart; Run, TIME TRAVEL or "Back to the date" send the arms back
              to the date. Fixing one: MANUAL, pick it, step it 1 or 10 deg at a time onto
              the line, SAVE HOME (tap twice); orrery.HOME_STEPS, ~/.orrery_home.json.
In a desktop browser the arrow keys, Enter
and T stand in for turn / press / today (the "turn", "press" and "hold" actions).

Only one program can use the servo bus: stop this one (sudo systemctl stop orrery)
before running servo_tool.py or orrery.py.
"""

import argparse
import collections
import json
import math
import os
import shutil
import signal
import subprocess
import threading
import time
import traceback
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import orrery as rig
from feetech import STATUS_BITS
from orrery import NUM_SERVOS, RUN_TICK, Arms, find_port, load_day, save_day
from planets import (BODY_NAMES, J2000, NUM_BODIES, ORBITS, cal_from_day, day_from_cal, planet_longitude,
                     year_text)

UI_DIR = Path(__file__).resolve().parent / "ui"
UI = UI_DIR / "index.html"
ADMIN = UI_DIR / "admin.html"
# Other files the screen loads from ui/ (three.js, the planet pages, their pictures).
PAGES = NUM_BODIES + 2      # PLANETS tab pages: 0 = the Sun, Mercury ... Mars, 5 = the asteroid belt (13 Nov 2026), Jupiter ... Pluto
SATURN = 7                  # the page the PLANETS tab opens on
PICKED = 4                  # Orrery.trip after Pick a date's GO: the row under the EVENTS (= len(EVENTS); ui/index.html)
STATIC_TYPES = {".js": "text/javascript; charset=utf-8", ".jpg": "image/jpeg", ".png": "image/png"}
SETTINGS_FILE = Path.home() / ".orrery_settings.json"
# Speed in years per minute, forward only (25 Sep: "no back in time, finer control").
# The screen slider sets any value in YPM_MIN..YPM_MAX; the arrow keys and the admin page's
# Slower/Faster step through STEPS.
# The only speeds (25 Sep: whole numbers, then "just jump to the next tick"): the
# slider snaps to these ticks, and the arrow keys / admin Slower-Faster step through them.
# Capped at 100 years a minute (7 Nov 2026, user: reliability, less risk of gears slipping;
# was 1000).
YPM_MIN, YPM_MAX = 1, 100
STEPS = [0, 1, 2, 5, 10, 20, 50, 100]


def nice(ypm):
    """Snap any requested speed to the nearest tick (compared on the log scale)."""
    if ypm < 0.5:
        return 0
    return min(STEPS[1:], key=lambda v: abs(math.log10(v) - math.log10(ypm)))


def step_from(ypm, n):
    """The STEPS value n clicks away from ypm (which may lie between two steps)."""
    if n > 0:
        i = next((k for k, v in enumerate(STEPS) if v > ypm + 1e-9), len(STEPS)) + n - 1
    else:
        i = max((k for k, v in enumerate(STEPS) if v < ypm - 1e-9), default=0) + n + 1
    return STEPS[min(max(i, 0), len(STEPS) - 1)]
CAP_RPM = 40                # no arm faster than this (measured no-load max ~50 rpm, 25 Sep)
# Racing arms keep their order (14 Nov 2026, user): each planet's top speed is this % of
# the one inside it, so at 100 yr/min Mercury 40 rpm > Venus 30 > Earth 22.5 > Mars 17
# instead of all four at 40. Jupiter's cap (12.7) is still above its 8.4 rpm at 100.
RACE_STEP_PCT = 75


def cap_rpm(b):
    """Fastest body b's arm may turn in Run mode: CAP_RPM for Mercury, then RACE_STEP_PCT % less per planet out."""
    return CAP_RPM * (RACE_STEP_PCT / 100.0) ** b
MEAN_DEG_PER_DAY = [o[9] / 36525.0 for o in ORBITS]    # each planet's average speed (JPL table)
# Manual mode (settings screen, 8 Nov 2026): the speed slider's ticks, in rpm of the
# servo (= the arm: the servo and tube gears are both 40T). Wheel mode cannot go below
# 50 steps/s (~0.7 rpm), so 1 rpm is the slowest.
MAN_RPM = [0, 1, 2, 3, 5, 10, 15, 20, 30, 40]
LAP_SECONDS = 7.5           # LINE UP and back: forward only, so up to a full turn (6.8 s at 600 steps/s)
NUDGE_DEG = (1, 10)         # MANUAL: the step buttons
MOVE_SECONDS = 4.5          # how long the screen says "moving" after GO / Today / TIME TRAVEL:
                            # a half turn at SERVO_SPEED 600 steps/s is ~3.4 s (was 2.5 at 2400)
RESCAN_SECONDS = 5          # look for servos that were off at start-up this often
# Typed dates (Pick a date): 1 AD - 3000 AD, the range of JPL's Table 2, in the calendar of
# the time (Julian before 1582), so a moment like 79 AD feeds straight in (14 Nov 2026, the
# user; was 1800-2200, and anything outside it opened on today).
PICK_YEARS = (1, 3000)
LO, HI = day_from_cal(PICK_YEARS[0], 1, 1), day_from_cal(PICK_YEARS[1], 12, 31)
RUN_LO, RUN_HI = day_from_cal(-2999, 1, 1), (date(9999, 12, 31) - J2000).days   # 3000 BC (JPL Table 2) on
# TIME TRAVEL (26 Sep, the user's list): (name, date in the calendar of the time, or
# years ago). ui/index.html has the words for each, in the same order. Before 1582 the
# dates are Julian, as history books give them.
# 7 Nov 2026 (user): Cambrian explosion, Dinosaur extinction and All nine in a line removed;
# Birth of Jesus (no exact day) replaced by the Miracle of the Sun at Fatima; 14 Nov 2026 (user: something
# from about then the kids enjoy) that became the Wright brothers' first flight; 16 Nov 2026 dropped
# (user: fewer rows, so the list takes less room).
EVENTS = [("Mt. Vesuvius eruption", (79, 8, 24), None), ("Declaration of Independence", (1776, 7, 4), None),
          ("Moon landing", (1969, 7, 20), None),
          ("Today", None, None)]


assert PICKED == len(EVENTS)


def event_day(k):
    """Day number (days since 2000-01-01) for EVENTS[k]."""
    name, cal, ago = EVENTS[k]
    if cal:
        return day_from_cal(*cal)
    if ago is None:
        return (date.today() - J2000).days
    return round(-ago * 365.25)        # deep time (no such event since 7 Nov 2026)
# Run mode may go far past 2200 at 100 years a minute; positions out there are only
# the JPL formula extrapolated, fine for a demo.


# Tuning knobs the admin page may change live: name -> (module, variable, min, max, what it does)
TUNABLES = {
    "cap_rpm":      ("server", "CAP_RPM", 10, 48, "Fastest Mercury's arm may turn in Run mode (rpm). Faster planets spin at their cap and are marked too fast."),
    "race_step":    ("server", "RACE_STEP_PCT", 50, 95, "Each planet's top speed as a % of the one inside it, so racing arms still go Mercury > Venus > Earth > Mars."),
    "wheel_slew":   ("rig", "WHEEL_SLEW", 50, 1000, "Ramp: most a spinning arm's speed may change per 0.1 s (steps/s). 250 = about 1 s from full speed to stop."),
    "wheel_kp":     ("rig", "WHEEL_KP", 0, 15, "How hard a spinning arm is steered back onto its planet (steps/s per step of error)."),
    "servo_speed":  ("rig", "SERVO_SPEED", 150, 600, "Speed of Time travel / Go-to-date / Today / settle-after-pause moves (steps/s; 4096 steps = 1 turn). Capped at 600 (7 Nov 2026) to spare the gears."),
    "torque_limit": ("rig", "SERVO_TORQUE_LIMIT", 100, 1000, "Servo power cap, 0-1000 = 0-100 %. It also caps top speed: 40 rpm needs ~750."),
}


def get_setting(name):
    mod, var = TUNABLES[name][:2]
    return (globals() if mod == "server" else vars(rig))[var]


def set_setting(name, value):
    mod, var, lo, hi = TUNABLES[name][:4]
    value = type(get_setting(name))(min(max(float(value), lo), hi))
    (globals() if mod == "server" else vars(rig))[var] = value
    return value


def load_settings():
    try:
        for k, v in json.loads(SETTINGS_FILE.read_text()).items():
            if k in TUNABLES:
                set_setting(k, v)
    except (OSError, ValueError):
        pass


def save_settings():
    try:
        SETTINGS_FILE.write_text(json.dumps({k: get_setting(k) for k in TUNABLES}, indent=1))
    except OSError:
        pass


def cpu_temp():
    try:
        return int(Path("/sys/class/thermal/thermal_zone0/temp").read_text()) / 1000
    except (OSError, ValueError):
        return None


# ---- Pi health (the screen's health tab, 26 Sep) ----
_cpu_prev = [None]                 # (idle, total) jiffies at the last look, for CPU %
_throttle = {"at": -99.0, "value": None}
# vcgencmd get_throttled bits: now (0-3) and since boot (16-19).
THROTTLE_BITS = {0: "under-voltage", 1: "speed capped", 2: "throttled", 3: "hot (soft limit)"}


def _read(path):
    try:
        return Path(path).read_text()
    except OSError:
        return None


def pi_stats():
    """How the Pi itself is doing. Values are None where the machine has no such file
    (a Mac in --dry-run)."""
    out = {"cpu_c": cpu_temp(), "cpu_pct": None, "mhz": None, "load": None, "mem_pct": None,
           "uptime_s": None, "disk_free_gb": None, "wifi_dbm": None, "throttled_now": None, "throttled_ever": None}
    stat = _read("/proc/stat")
    if stat:
        f = [int(x) for x in stat.split("\n")[0].split()[1:]]
        idle, total = f[3] + f[4], sum(f)
        prev, _cpu_prev[0] = _cpu_prev[0], (idle, total)
        if prev and total > prev[1]:
            out["cpu_pct"] = round(100 * (1 - (idle - prev[0]) / (total - prev[1])))
    if (khz := _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")):
        out["mhz"] = int(khz) // 1000
    if hasattr(os, "getloadavg"):
        out["load"] = round(os.getloadavg()[0], 2)
    if (mem := _read("/proc/meminfo")):
        kb = {line.split(":")[0]: int(line.split()[1]) for line in mem.splitlines() if line.split()[1:]}
        if kb.get("MemTotal"):
            out["mem_pct"] = round(100 * (1 - kb.get("MemAvailable", 0) / kb["MemTotal"]))
    if (up := _read("/proc/uptime")):
        out["uptime_s"] = round(float(up.split()[0]))
    out["disk_free_gb"] = round(shutil.disk_usage("/").free / 1e9, 1)
    for line in (_read("/proc/net/wireless") or "").splitlines()[2:]:
        parts = line.split()
        if parts and parts[0].startswith("wlan"):
            out["wifi_dbm"] = int(float(parts[3]))
    # Throttling: asking the firmware takes a few ms, so at most every 5 s.
    if time.monotonic() - _throttle["at"] > 5:
        _throttle["at"] = time.monotonic()
        try:
            txt = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=2).stdout
            _throttle["value"] = int(txt.strip().split("=")[1], 16)
        except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
            _throttle["value"] = None
    v = _throttle["value"]
    if v is not None:
        out["throttled_now"] = [name for bit, name in THROTTLE_BITS.items() if v & (1 << bit)]
        out["throttled_ever"] = [name for bit, name in THROTTLE_BITS.items() if v & (1 << (bit + 16))]
    return out


def to_date(day):
    return J2000 + timedelta(days=round(day))


def remember(day):
    """Save the date for the next start-up (not BC dates or deep time: those start at the last AD one)."""
    try:
        save_day(to_date(day))
    except (OverflowError, ValueError):
        pass


def ymd(day):
    """[year, month, day] for editing in place, in the calendar of the time: typed dates stay in PICK_YEARS."""
    return cal_from_day(min(max(day, LO), HI))


class Orrery:
    """All state lives here; the web handlers only call act()."""

    def __init__(self, arms):
        self.arms = arms
        self.lock = threading.Lock()
        self.day = float((load_day() - J2000).days)
        self.mode = "run"                  # the tab on screen: "run", "planets", "travel", "galaxy", "scale" or "health"
        self.planet = SATURN               # PLANETS tab page: 0 = Sun, 1 = Mercury ...; opens on Saturn
        self.ypm = 2                       # years per minute the planets run at
        self.ypm_set = 2                   # the speed chosen on the slider; applied on release or by Run
        self.t_day = time.monotonic()      # when self.day was last advanced
        self.editing = None                # RUN screen: 0/1/2 = editing day/month/year in place
        self.paused = True
        self.trip = None                   # TIME TRAVEL: the event the arms were sent to (index), until the date changes
        self.deep = None                   # years ago, while showing an event too long ago for real positions
        self.entry = ymd(self.day)
        self.field = 0
        self.run_from = None             # (day, true angles) where the current run started
        self.racing = [False] * NUM_BODIES
        self.run_lon = None
        self.was_running = False
        self.aim_pending = True          # put the arms on the saved date at start-up
        self.moving_until = time.monotonic() + MOVE_SECONDS   # arms go to the saved date first
        self.error = ""
        self.started = time.monotonic()
        self.taps = collections.deque(maxlen=40)
        self.admin_seen = 0.0              # servo readings are only polled while /admin is open
        self.health_seen = 0.0             # ... or the screen's health tab
        self.readings = [None] * NUM_SERVOS
        self.readings_at = None            # when the last full readings were taken
        self.loop_ms = collections.deque(maxlen=100)   # recent motion-loop periods (~10 s)
        self.off = False                   # "Turn off" tapped: stopping, then the Pi shuts down
        self.shutdown = None               # main() sets this; tests and the website leave it None
        # Manual mode (settings screen): off at start-up since 7 Nov 2026 (the user: start
        # on AUTO); was on during the build so nothing moved until AUTO was tapped.
        self.manual = False
        self.man_sel = [False] * NUM_SERVOS   # planets picked in the servo list
        self.man_rpm = 0                      # slider: 0 = stopped
        self.man_dir = 1                      # 1 = the way the planets go (counter-clockwise from above), -1 = back
        self.handback = False                 # just switched to AUTO: stop any manual spin, then settle on the date
        self.start_aim = True                 # the first aim after start-up leaves arms nearly there alone (rig.START_HOLD_DEG)
        self.parked = False                   # the program is stopping: the motion loop leaves the arms alone
        self.lined_up = False                 # LINE UP: arms out over the screen, not on the date (main() reads the saved one)
        self.note, self.note_at = "", -99.0   # a few seconds of feedback on the settings screen (SAVE HOME)

    # ---- what the screen can do ----

    def running(self):
        return not self.paused and self.ypm > 0     # keeps running on the PLANETS tab

    def _jump(self, day, deep=None):
        self.day = float(day if deep else min(max(day, RUN_LO), RUN_HI))
        self.deep, self.trip = deep, None
        self.paused = True
        self.aim_pending = True
        self.moving_until = time.monotonic() + MOVE_SECONDS
        remember(self.day)

    def _line(self, on):
        """TRAVEL MODE (was LINE UP) on or off: the arms go to the line (or back to the date), forward only."""
        self.lined_up = on
        self.paused, self.trip = True, None
        self.aim_pending = True
        self.moving_until = time.monotonic() + LAP_SECONDS
        rig.save_home(on)

    def _nudge(self, field, n):
        y, m, d = self.entry
        if field == 0:
            y, m, d = cal_from_day(day_from_cal(y, m, min(d, _dim(y, m))) + n)
        elif field == 1:
            months = y * 12 + m - 1 + n
            y, m = months // 12, months % 12 + 1
        else:
            # Typed years stay in the JPL table's good range. Only clamp when the year
            # itself is changed, so fixing the day of a run-mode date like 2255 is fine.
            y = min(max(y + n, PICK_YEARS[0]), PICK_YEARS[1])
        self.entry = [y, m, min(d, _dim(y, m))]

    def act(self, a):
        what = a.get("do")
        with self.lock:
            if what != "nudge" and what != "edit":
                edit_was, self.editing = self.editing, None   # most taps end an in-place edit
            if self.lined_up and (what in ("travel", "go", "today", "hold", "press") or
                                  (what == "speed" and a.get("apply"))):
                # Lined up, and someone wants the date back: the arms go there first (so a
                # Run tap is used up while they move; GO / TIME TRAVEL / Today just go).
                self._line(False)
            if what == "tab":
                # "system" (the old SOLAR SYSTEM tab, now RUN) and anything unknown -> "run"
                mode = a.get("mode") if a.get("mode") in ("planets", "travel", "galaxy", "scale", "health") else "run"
                if mode == "planets" and self.mode != "planets":
                    self.planet = SATURN    # the PLANETS tab always opens on Saturn (user, 26 Sep)
                if mode in ("travel", "run") and self.manual:
                    self._set_manual(False)  # TIME MACHINE and ORBITS are ready to go: back to AUTO (14 Nov 2026, the user)
                self.mode = mode
            elif what == "planet":          # PLANETS tab: tapped the Sun's or a planet's name
                self.planet = int(a.get("n", 0)) % PAGES
            elif what == "travel":          # TIME TRAVEL tab: tapped an event
                self._travel(int(a.get("n", 0)) % len(EVENTS))
            elif what == "edit":            # TIME TRAVEL: "Pick a date", or tapped its day, month or year
                if self.mode == "travel":
                    if self.running():
                        self.paused = True  # stop first; the arms settle while the date is picked
                    if self.editing is None:
                        # A fresh pick starts at the date the planets are on: where Run was
                        # paused, or the last date gone to (user, 13 Nov 2026; was today).
                        # Outside the years that can be picked (a far Run, deep time): today.
                        here = LO <= self.day <= HI and not self.deep
                        self.entry = ymd(self.day if here else (date.today() - J2000).days)
                    self.trip = None
                    self.editing = self.field = int(a.get("field", 0)) % 3
            elif what == "turn":
                n = int(a.get("n", 0))
                if edit_was is not None:    # arrow keys while editing in place: change that part
                    self.editing = edit_was
                    self._nudge(edit_was, n)
                elif self.mode == "run":
                    self.ypm_set = step_from(self.ypm_set, n)   # chosen only; Run applies it
                elif self.mode == "travel":
                    self._travel(((self.trip if self.trip is not None and self.trip < len(EVENTS) else len(EVENTS) - 1) + n) % len(EVENTS))
                else:
                    self.planet = (self.planet + n) % PAGES
            elif what == "speed":           # the slider on the screen: any speed
                self.ypm_set = nice(max(float(a.get("ypm", self.ypm_set)), 0))   # while dragging: chosen only
                if a.get("apply"):
                    # Let go of the slider (26 Sep, user: "when released, not while being
                    # changed ... no need to press the green button"): the speed takes
                    # effect at once. Stop = pause; paused = start at it (not while the arms
                    # are still settling on a date, nor in deep time: Run stays for that).
                    if self.ypm_set == 0:
                        self.paused = True
                    elif self.running():
                        self.ypm = self.ypm_set
                    elif time.monotonic() >= self.moving_until and not self.deep:
                        self.ypm = self.ypm_set
                        self.paused = False
                        self.trip = None
            elif what == "press" and edit_was is not None:     # Enter while editing = GO
                y, m, d = self.entry
                self._jump(day_from_cal(y, m, d))
                self.trip = PICKED
            elif what == "cancel":
                pass
            elif what == "manual":          # settings: the MANUAL / AUTO switch
                self._set_manual(bool(a.get("on")))
            elif what == "mpick":           # manual: tap a planet in the servo list (or all / none)
                if self.manual:
                    if "all" in a:
                        self.man_sel = [bool(a["all"])] * NUM_SERVOS
                    else:
                        k = int(a.get("p", 0))
                        if 0 <= k < NUM_SERVOS:
                            self.man_sel[k] = not self.man_sel[k]
            elif what == "mspeed":          # manual: the rpm slider (applies at once)
                if self.manual:
                    rpm = max(float(a.get("rpm", 0)), 0)
                    self.man_rpm = min(MAN_RPM, key=lambda v: abs(v - rpm))
            elif what == "mdir":            # manual: forward (the planets' way) or reverse
                if self.manual:
                    self.man_dir = -1 if int(a.get("dir", 1)) < 0 else 1
            elif what == "mstop":           # manual: STOP (ramps down, then limp)
                self.man_rpm = 0
                if self.arms:
                    self.arms.release()
            elif what == "lineup":          # settings (AUTO): LINE UP / Back to the date
                on = bool(a.get("on"))
                if on != self.lined_up:
                    self._line(on)
            elif what == "mnudge":          # manual: step the picked arms 1 or 10 deg (the arrow's way)
                deg = min(NUDGE_DEG, key=lambda v: abs(v - abs(float(a.get("deg", 1)))))
                if self.manual and self.arms and not self.man_rpm:
                    delta = round(deg * rig.STEPS_PER_TURN / 360) * self.man_dir * rig.ARM_DIR
                    for p in range(NUM_SERVOS):
                        if self.man_sel[p]:
                            self.arms.nudge(p, delta)
            elif what == "home":            # manual: SAVE HOME, the picked arms are on the line
                if self.manual and self.arms:
                    saved = []
                    for p in range(NUM_SERVOS):
                        if self.man_sel[p] and self.arms.ok[p] and not self.arms.wheel[p]:
                            try:
                                rig.HOME_STEPS[p] = self.arms.reading(p)
                                saved.append(BODY_NAMES[p])
                            except Exception as e:
                                print(f"SAVE HOME {BODY_NAMES[p]}: {e}", flush=True)
                    if saved:
                        rig.zero_from_home()
                        rig.save_home(self.lined_up)
                    self.note = ("Home saved: " + ", ".join(saved)) if saved else "Nothing saved (pick a stopped planet)"
                    self.note_at = time.monotonic()
            elif what == "unhome":          # manual: RESET HOME, forget the picked arms' saved homes
                # (16 Nov 2026, the user: an arm that drifted and was put right by hand, with a
                # tool, on its tube). Back to the built-in home: the servo step that stands
                # for HOME_LON, where the arm was clamped on in travel mode.
                if self.manual:
                    gone = [BODY_NAMES[p] for p in range(NUM_SERVOS) if self.man_sel[p] and rig.HOME_STEPS[p] is not None]
                    for p in range(NUM_SERVOS):
                        if self.man_sel[p]:
                            rig.HOME_STEPS[p] = None
                    if gone:
                        rig.zero_from_home()
                        rig.save_home(self.lined_up)
                    self.note = ("Home reset: " + ", ".join(gone)) if gone else "Nothing to reset (no saved home picked)"
                    self.note_at = time.monotonic()
            elif what == "poweroff":
                # The screen's Turn off button (27 Sep 2026, battery build): the planets stop
                # and settle, the date is saved, then the Pi shuts down. The screen says to
                # wait until it goes dark before flipping the switch, so the SD card is safe.
                if not self.off:
                    self.off, self.paused, self.trip = True, True, None
                    self.man_rpm = 0
                    if self.shutdown:
                        threading.Thread(target=self.shutdown, daemon=True).start()
            elif what == "press":
                # Run / Pause. Run starts at the chosen speed; a speed chosen with the
                # arrow keys or admin page while running is applied by the same button. (The
                # slider applies its speed itself when let go, since 26 Sep.)
                if time.monotonic() < self.moving_until and not self.running():
                    pass                        # arms still settling on a date: Run would start them off-target
                elif self.deep:
                    pass                        # no running on from 66 million years ago: pick a date or Today
                elif self.running() and self.ypm_set not in (0, self.ypm):
                    self.ypm = self.ypm_set
                elif self.running():
                    self.paused = True
                else:
                    if self.ypm_set == 0:
                        self.ypm_set = 2
                    self.ypm = self.ypm_set
                    self.paused = False
                    self.trip = None
            elif what in ("hold", "today"):
                self._jump((date.today() - J2000).days)
                self.entry = ymd(self.day)
            elif what == "nudge":
                self.field = int(a.get("field", 0)) % 3
                if self.editing is not None:
                    self.editing = self.field
                self._nudge(self.field, int(a.get("n", 0)))
            elif what == "go":
                y, m, d = self.entry
                self._jump(day_from_cal(y, m, d))
                self.trip = PICKED          # TIME TRAVEL shows it as "Your date", Pick a date lit
            else:
                return {"error": f"unknown action {what!r}"}
        return {"ok": True}

    def _set_manual(self, on):
        """The MANUAL / AUTO switch. Back to AUTO, every arm goes to the date (or the
        travel-mode row) once any manual spin has ramped down (tick: handback)."""
        if on != self.manual:
            self.manual = on
            self.man_rpm = 0
            self.handback = not on
            if self.arms:
                self.arms.hold = not on   # servos found later: limp in manual
                self.arms.release()

    def _travel(self, k):
        name, cal, ago = EVENTS[k]
        self._jump(event_day(k), deep=ago)
        self.trip = k
        if not ago:
            self.entry = ymd(self.day)

    def state(self):
        with self.lock:
            y, m, dd = cal_from_day(self.day)
            arms = self.arms
            running = self.running()
            lon = self.run_lon if running and self.run_lon else \
                [planet_longitude(b, self.day) for b in range(NUM_BODIES)]
            if self.lined_up and not running:   # travel mode: the picture shows the row too
                lon = [rig.HOME_LON] * NUM_SERVOS + lon[NUM_SERVOS:]
            return {
                "mode": self.mode, "planet": self.planet, "running": running, "paused": self.paused,
                "years_per_min": self.ypm, "ypm_set": self.ypm_set,
                "ypm_min": YPM_MIN, "ypm_max": YPM_MAX, "steps": STEPS,
                "racing": self.racing if running else [False] * NUM_BODIES,
                "date": f"{self.deep / 1e6:,.0f} million years ago" if self.deep else
                        f"{dd} {date(2000, m, 1):%b} {year_text(y)}",
                "ymd": [y, m, dd], "trip": self.trip, "deep": self.deep, "off": self.off,
                "entry": self.entry, "field": self.field, "editing": self.editing,
                "moving": time.monotonic() < self.moving_until,
                "lon": [round(a, 2) for a in lon],
                # The date as of this moment (the loop only advances it every ~0.1 s);
                # the screen animates on from here until its next poll.
                "day": round(self.day + (self.ypm * 365.25 / 60.0 * (time.monotonic() - self.t_day)
                                         if running else 0), 4),
                "mean": [round(v, 9) for v in MEAN_DEG_PER_DAY],
                "names": BODY_NAMES,
                "servos": [bool(ok) for ok in arms.ok] if arms else [],
                "servo_names": BODY_NAMES[:NUM_SERVOS],
                "manual": self.manual,
                "lined_up": self.lined_up,
                "home_set": [h is not None for h in rig.HOME_STEPS],
                "note": self.note if time.monotonic() - self.note_at < 6 else "",
                "man": {"sel": list(self.man_sel), "rpm": self.man_rpm, "dir": self.man_dir, "steps": MAN_RPM},
                "error": self.error,
            }

    # ---- the motion loop ----

    def man_spin(self):
        """Manual mode: each servo's wheel speed (steps/s), 0 for the ones not picked."""
        sps = round(self.man_rpm * rig.STEPS_PER_TURN / 60) * self.man_dir * rig.ARM_DIR
        return [sps if on else 0 for on in self.man_sel]

    def park(self):
        """systemctl stop / restart / reboot (SIGTERM): spinning arms ramp down and every
        arm holds where it is, then the date is saved, so the next start-up finds the arms
        already on it and leaves them be (7 Nov 2026: the arms moved at every restart)."""
        with self.lock:
            self.parked = True
            if self.arms:
                self.arms.park()
            if not self.deep:
                remember(self.day)

    def tick(self, dt):
        with self.lock:
            if self.parked:
                return
            # Manual: only the settings screen drives the servos; the date logic below
            # still runs (the screen animates) but with no arms. Back to AUTO: let any
            # manual spin ramp down first, then settle every arm on the date.
            if self.manual:
                if self.arms:
                    self.arms.manual(self.man_spin())
            elif self.handback:
                if self.arms and not self.arms.ramp_down():
                    return
                self.handback = False
                self.aim_pending = True
            arms = None if self.manual else self.arms
            if self.running():
                if self.run_from is None:
                    self.run_from = (self.day, [planet_longitude(b, self.day) for b in range(NUM_BODIES)])
                days_per_s = self.ypm * 365.25 / 60.0
                self.day += days_per_s * dt
                self.t_day = time.monotonic()
                if not RUN_LO <= self.day <= RUN_HI:
                    self.day = min(max(self.day, RUN_LO), RUN_HI)
                    self.paused = True
                # Circular orbits: angle = true angle at the start + average speed x time.
                # Targets depend only on the date, so changing speed mid-run never jumps.
                day0, lon0 = self.run_from
                lon, rate, racing = [], [], []
                for b in range(NUM_BODIES):
                    cap = cap_rpm(b) * 6.0                           # degrees per second
                    r = MEAN_DEG_PER_DAY[b] * days_per_s
                    racing.append(abs(r) > cap)
                    lon.append((lon0[b] + MEAN_DEG_PER_DAY[b] * (self.day - day0)) % 360.0)
                    rate.append(max(-cap, min(cap, r)))
                self.racing, self.run_lon = racing, lon
                if arms:
                    arms.follow([None if rc else a for a, rc in zip(lon, racing)], rate)
                self.was_running = True
            elif self.was_running:
                # Just stopped: ramp the spinning arms down over ~1 s (a tick at a time,
                # so the screen stays live), then settle every arm exactly on the date.
                if arms and not arms.ramp_down():
                    return
                self.was_running = False
                self.run_from = None
                self.run_lon = None          # else the next Run reports this run's end for a tick (test_server.py)
                self.racing = [False] * NUM_BODIES
                self.aim_pending = True
                remember(self.day)
            if self.aim_pending and not self.manual:
                self.aim_pending = False
                if arms:
                    arms.stop()
                    hold = rig.START_HOLD_DEG if self.start_aim else rig.AIM_HOLD_DEG
                    self.start_aim = False
                    arms.aim([rig.HOME_LON] * NUM_BODIES if self.lined_up else
                             [planet_longitude(b, self.day) for b in range(NUM_BODIES)], hold)   # forward only

    def read_servos(self):
        """Readings for the admin page and the health tab, every 0.5 s while either is
        open (the user's ask, 2 Oct 2026). While the planets run, the motion loop already
        reads every servo each tick (Arms.live), so those are used; otherwise one snapshot()
        read each (~0.6 ms: small enough to take while arms settle, unlike the old 8-read
        status())."""
        with self.lock:
            fresh = self.running() and not self.manual     # the loop reads every arm itself
            for p in range(NUM_SERVOS):
                if self.arms and self.arms.ok[p]:
                    if (fresh or self.arms.wheel[p]) and self.arms.live[p]:
                        self.readings[p] = self.arms.live[p]
                        continue
                    try:
                        self.readings[p] = self.arms.bus.snapshot(rig.SERVO_ID[p])
                    except Exception as e:
                        self.readings[p] = {"error": str(e)}
                else:
                    self.readings[p] = None
            self.readings_at = time.monotonic()

    def health(self):
        """The screen's health tab: the Pi, the motion loop and each servo."""
        self.health_seen = time.monotonic()
        running = self.running()
        arms, loop = self.arms, list(self.loop_ms)
        servos = []
        for p in range(NUM_SERVOS):
            r = self.readings[p] or {}
            line = rig.from_line(p, r.get("position")) if arms and arms.ok[p] else None
            servos.append({
                "name": BODY_NAMES[p], "id": rig.SERVO_ID[p], "connected": bool(arms and arms.ok[p]),
                "spinning": bool(arms and arms.ok[p] and arms.wheel[p]),
                "limp": bool(arms and arms.ok[p] and arms.limp[p]),
                "off_deg": round(arms.err_deg[p], 1) if arms and arms.ok[p] and running and not self.manual else None,
                "temp_c": r.get("temp_c"), "volts": r.get("volts"),
                "position": r.get("position"),       # raw encoder count, multi-turn (4096 a turn)
                "home_set": rig.HOME_STEPS[p] is not None,
                "line_deg": line if line is None else round(line, 1),   # from the LINE UP position
                "load_pct": r.get("load_per_mille", 0) / 10 if "load_per_mille" in r else None,
                "current_ma": r.get("current_ma"),
                "rpm": round(r["speed"] * 60 / 4096, 1) if "speed" in r else None,
                # the servo's own protections that have switched its motor off (feetech.STATUS_BITS)
                "tripped": [name for bit, name in STATUS_BITS.items() if r.get("status", 0) & bit],
                "error": r.get("error"),
            })
        return {
            "pi": pi_stats(), "servos": servos, "running": running, "dry_run": arms is None, "manual": self.manual,
            "readings_age_s": round(time.monotonic() - self.readings_at) if self.readings_at else None,
            "loop_ms": {"avg": round(sum(loop) / len(loop)), "max": round(max(loop))} if loop else None,
            "server_up_s": round(time.monotonic() - self.started), "error": self.error,
        }

    def admin(self):
        self.admin_seen = time.monotonic()
        st = self.state()
        arms = self.arms
        rows = []
        for p in range(NUM_SERVOS):
            r = self.readings[p] or {}
            rows.append({
                "id": rig.SERVO_ID[p], "name": BODY_NAMES[p],
                "connected": bool(arms and arms.ok[p]),
                "mode": ("limp" if arms.limp[p] else "wheel" if arms.wheel[p] else "position") if arms and arms.ok[p] else None,
                "racing": st["racing"][p], "target_deg": st["lon"][p],
                "at_deg": round(r["position"] % 4096 * 360 / 4096, 1) if "position" in r else None,
                "err_deg": round(arms.err_deg[p], 1) if arms and st["running"] else None,
                "rpm": round(r["speed"] * 60 / 4096, 1) if "speed" in r else None,
                "cmd_rpm": round(arms.cmd[p] * 60 / 4096, 1) if arms and arms.wheel[p] else None,
                "load_pct": r.get("load_per_mille", 0) / 10 if "load_per_mille" in r else None,
                "volts": r.get("volts"), "temp_c": r.get("temp_c"), "error": r.get("error"),
            })
        return {
            "state": st, "servos": rows, "taps": list(self.taps)[::-1],
            "settings": {k: {"value": get_setting(k), "min": t[2], "max": t[3], "help": t[4]} for k, t in TUNABLES.items()},
            "pi": {"cpu_c": cpu_temp(), "server_up_s": round(time.monotonic() - self.started),
                   "dry_run": arms is None},
        }

    def change(self, new):
        out = {}
        with self.lock:
            for k, v in new.items():
                if k in TUNABLES:
                    out[k] = set_setting(k, v)
                    if k == "torque_limit" and self.arms:
                        for p in range(NUM_SERVOS):
                            if self.arms.ok[p]:
                                self.arms.bus.set_torque_limit(rig.SERVO_ID[p], out[k])
            save_settings()
        return out

    def loop(self):
        last = next_scan = next_read = time.monotonic()
        slow = False                         # the last pass looked for missing servos (slow on purpose, only while paused)
        while True:
            now = time.monotonic()
            if not slow:                     # the health tab shows the loop's normal timing
                self.loop_ms.append((now - last) * 1000)
            slow = False
            try:
                # Looking for a missing servo waits ~50 ms per ID for a reply that never
                # comes, freezing the loop (25 Sep: a 257 ms stall every 5 s made the
                # arms jerk and whine at 2 yr/min). So only look while nothing moves.
                idle = (not any(self.man_spin()) and not any(self.arms.wheel) if self.manual and self.arms else
                        not self.running() and not self.was_running and now >= self.moving_until)
                if self.arms and idle and now >= next_scan and not all(self.arms.ok):
                    next_scan = now + RESCAN_SECONDS
                    slow = True
                    with self.lock:
                        found = self.arms.rescan()
                        if found:
                            print("servos found:", [BODY_NAMES[p] for p in found], flush=True)
                            self.aim_pending = not self.manual
                self.tick(now - last)
                # Servo readings for the admin page or the screen's health tab, twice a second.
                if (now - self.admin_seen < 5 or now - self.health_seen < 5) and now >= next_read:
                    next_read = now + 0.5
                    self.read_servos()
                self.error = ""
            except Exception as e:          # a loose cable must not kill the loop
                self.error = f"{type(e).__name__}: {e}"
                traceback.print_exc()
                time.sleep(1)
            last = now
            time.sleep(RUN_TICK)


def _dim(y, m):
    """Days in the month, in the calendar of the time (Julian leap years before 1582)."""
    return round(day_from_cal(y + m // 12, m % 12 + 1, 1) - day_from_cal(y, m, 1))


def static_files():
    """ui/ files the screen may load, by URL path (a fixed list: no path tricks)."""
    return {str(f.relative_to(UI_DIR)): STATIC_TYPES[f.suffix] for f in UI_DIR.rglob("*")
            if f.suffix in STATIC_TYPES and f.is_file()}


def power_off(orrery, dry_run):
    """After Turn off: wait for the arms to stop and settle (at most ~10 s), save the
    date, then shut the Pi down. The screen goes dark at the very end of shutdown
    (setup/blank-screen, a systemd-shutdown hook), which is the sign to flip the switch."""
    end = time.monotonic() + 10
    while time.monotonic() < end and (orrery.was_running or time.monotonic() < orrery.moving_until):
        time.sleep(0.2)
    if not orrery.deep:
        remember(orrery.day)
    print("turn off: shutting the Pi down" + (" (dry run: not really)" if dry_run else ""), flush=True)
    if dry_run:
        time.sleep(6)
        orrery.off = False            # on a laptop, come back so testing can go on
        return
    subprocess.run(["sudo", "-n", "systemctl", "poweroff"], check=False)


def make_handler(orrery):
    STATIC = static_files()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, kind="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]      # the kiosk opens /?kiosk
            if path in ("/", "/index.html"):
                self._send(200, UI.read_bytes(), "text/html; charset=utf-8")
            elif path[1:] in STATIC and (f := UI_DIR / path[1:]).is_file():
                self._send(200, f.read_bytes(), STATIC[path[1:]])
            elif path == "/admin":
                self._send(200, ADMIN.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/admin":
                self._send(200, orrery.admin())
            elif path == "/api/state":
                self._send(200, orrery.state())
            elif path == "/api/health":
                self._send(200, orrery.health())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            path = self.path.split("?")[0]
            if path not in ("/api/action", "/api/admin"):
                return self._send(404, {"error": "not found"})
            try:
                a = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                return self._send(400, {"error": "bad JSON"})
            if path == "/api/admin":
                print("settings:", json.dumps(a), flush=True)
                return self._send(200, orrery.change(a.get("set", {})))
            print("tap:", json.dumps(a), flush=True)   # journalctl -u orrery shows what the screen sent
            orrery.taps.append({"t": time.strftime("%H:%M:%S"), "from": self.client_address[0], "do": a})
            self._send(200, orrery.act(a))

        def log_message(self, *args):
            pass                             # 5 polls a second would flood the journal

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--serial", help="servo driver board serial port (default: auto-detect)")
    ap.add_argument("--dry-run", action="store_true", help="no servos")
    args = ap.parse_args()

    load_settings()
    lined_up = rig.load_home()          # the arms' calibration, and whether they were left lined up
    print("home steps:", rig.HOME_STEPS, "lined up" if lined_up else "", flush=True)
    arms = None
    if not args.dry_run:
        from feetech import Bus
        arms = Arms(Bus(args.serial or find_port()))   # starts in AUTO: torque on, arms go to the saved date
    orrery = Orrery(arms)
    orrery.lined_up = lined_up          # left lined up (for carrying): start-up keeps them there
    orrery.shutdown = lambda: power_off(orrery, args.dry_run)
    threading.Thread(target=orrery.loop, daemon=True).start()

    def stopping(signum, frame):        # systemd stop / restart / reboot, or Ctrl-C
        print("stopping: arms held where they are, date saved", flush=True)
        orrery.park()
        os._exit(0)
    signal.signal(signal.SIGTERM, stopping)
    signal.signal(signal.SIGINT, stopping)
    server = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(orrery))
    print(f"orrery screen on http://0.0.0.0:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
