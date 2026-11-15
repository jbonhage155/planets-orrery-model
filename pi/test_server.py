#!/usr/bin/env python3
"""Checks for the touchscreen server's rules, no servos needed:   python3 test_server.py

Drives server.Orrery with no servos (as --dry-run) and a fake clock, so nothing waits
and nothing is saved: the saved date (~/.planet_dial.json) is not touched. Then plays
the same taps through ui/sim.js (the website's copy of these rules, run in node) and
checks both give the same screen state; skipped when node is not installed (the Pi).
(TODO.md item 11, 26 Sep 2026.)
"""

import json
import shutil
import subprocess
import time as real_time
import types
from datetime import date
from pathlib import Path

import orrery as rig
import server
from planets import shortest_turn

failures = 0


def check(ok, msg):
    global failures
    if not ok:
        failures += 1
        print("FAIL:", msg)


# A fake clock and no saving, before any Orrery is made.
NOW = [1000.0]
server.time = types.SimpleNamespace(monotonic=lambda: NOW[0], sleep=lambda s: None, strftime=real_time.strftime)
server.load_day = date.today
server.save_day = lambda d: None
import tempfile
rig.HOME_FILE = Path(tempfile.mkdtemp()) / "home.json"     # the Pi's real calibration is never touched


def fresh():
    o = server.Orrery(None)
    wait(o, 5)                      # past the start-up "moving to the saved date"
    return o


def wait(o, secs):
    """Let `secs` seconds pass, the motion loop ticking every 0.1 s as on the Pi."""
    for _ in range(round(secs * 10)):
        NOW[0] += 0.1
        o.tick(0.1)


def st(o):
    return o.state()


# ---- Turn off (27 Sep 2026) -----------------------------------------------------
o = fresh()
calls = []
o.shutdown = lambda: calls.append(1)
o.act({"do": "press"})
wait(o, 2)
check(st(o)["running"] and not st(o)["off"], "running before Turn off")
o.act({"do": "poweroff"})
real_time.sleep(0.05)               # the shutdown runs in its own thread
check(st(o)["off"] and not st(o)["running"], "Turn off stops the planets and says so")
o.act({"do": "poweroff"})
real_time.sleep(0.05)
check(calls == [1], f"Turn off starts the shutdown once (started {len(calls)} times)")

# ---- speed steps --------------------------------------------------------------
check(server.nice(0.2) == 0 and server.nice(3) == 2 and server.nice(4) == 5 and server.nice(700) == 100, "nice() snaps to ticks")
check(server.step_from(2, 1) == 5 and server.step_from(2, -1) == 1 and server.step_from(0, 1) == 1, "step_from() one click")
check(server.step_from(3, 1) == 5 and server.step_from(3, -1) == 2, "step_from() between ticks")
check(server.step_from(100, 1) == 100 and server.step_from(0, -1) == 0, "step_from() stops at the ends")

# ---- slider: dragging only chooses, letting go applies --------------------------
o = fresh()
o.act({"do": "speed", "ypm": 50})
s = st(o)
check(not s["running"] and s["ypm_set"] == 50 and s["years_per_min"] == 2, "dragging the slider only chooses")
o.act({"do": "speed", "ypm": 50, "apply": True})
s = st(o)
check(s["running"] and s["years_per_min"] == 50, "letting go while paused starts at that speed")
wait(o, 1)
o.act({"do": "speed", "ypm": 100})
check(st(o)["years_per_min"] == 50, "dragging while running does not change the speed yet")
o.act({"do": "speed", "ypm": 100, "apply": True})
check(st(o)["running"] and st(o)["years_per_min"] == 100, "letting go while running switches speed")
o.act({"do": "speed", "ypm": 1000, "apply": True})
check(st(o)["years_per_min"] == 100, "nothing faster than 100 years a minute")
o.act({"do": "speed", "ypm": 0, "apply": True})
check(not st(o)["running"], "letting go on the stop notch pauses")
wait(o, 2)

o = fresh()
o.act({"do": "today"})                               # arms now "moving" for 4.5 s
o.act({"do": "speed", "ypm": 10, "apply": True})
check(not st(o)["running"] and st(o)["ypm_set"] == 10, "slider release does not start while the arms settle")
wait(o, 5)
o.act({"do": "speed", "ypm": 10, "apply": True})
check(st(o)["running"], "slider release starts once settled")

# ---- knob: turn chooses, press (Run) applies; Run ignored while settling ----------
o = fresh()
o.act({"do": "turn", "n": 1})
s = st(o)
check(not s["running"] and s["ypm_set"] == 5, "knob turn on RUN only chooses")
o.act({"do": "press"})
check(st(o)["running"] and st(o)["years_per_min"] == 5, "Run starts at the chosen speed")
o.act({"do": "turn", "n": 1})
check(st(o)["years_per_min"] == 5 and st(o)["ypm_set"] == 10, "knob turn while running waits for Run at")
o.act({"do": "press"})
check(st(o)["years_per_min"] == 10 and st(o)["running"], "Run at applies the knob's choice")
o.act({"do": "press"})
check(not st(o)["running"], "Pause")
o = fresh()
o.act({"do": "today"})
o.act({"do": "press"})
check(not st(o)["running"], "Run ignored while the arms settle on a date")

# ---- in-place date editing -------------------------------------------------------
o = fresh()
o.act({"do": "edit", "field": 0})
check(st(o)["editing"] is None, "no date picking on the RUN tab")
o.act({"do": "tab", "mode": "travel"})
o.act({"do": "speed", "ypm": 2, "apply": True})
o.act({"do": "edit", "field": 0})
check(st(o)["editing"] == 0 and not st(o)["running"], "TIME TRAVEL: Pick a date while running pauses and edits the day")
wait(o, 5)
o.act({"do": "edit", "field": 0})
check(st(o)["editing"] == 0, "tap the day while paused edits it")
o.entry = [2025, 12, 31]
o.act({"do": "nudge", "field": 0, "n": 1})
check(st(o)["entry"] == [2026, 1, 1], "day roll-over into a new year")
o.act({"do": "nudge", "field": 2, "n": 2000})
check(st(o)["entry"][0] == 3000, "typed years stop at 3000 AD")
o.act({"do": "nudge", "field": 2, "n": -5000})
check(st(o)["entry"][0] == 1, "typed years stop at 1 AD")
o.entry = [100, 2, 28]                               # Julian: 100 AD is a leap year
o.act({"do": "nudge", "field": 0, "n": 1})
check(st(o)["entry"] == [100, 2, 29], f"day steps use the calendar of the time (29 Feb 100 AD) ({st(o)['entry']})")
o.entry = [1582, 10, 4]                              # the day before the calendar changed
o.act({"do": "nudge", "field": 0, "n": 1})
check(st(o)["entry"] == [1582, 10, 15], f"4 Oct 1582 + 1 day = 15 Oct 1582 ({st(o)['entry']})")
o.entry = [2255, 3, 30]
o.act({"do": "nudge", "field": 0, "n": 1})
check(st(o)["entry"] == [2255, 3, 31], "fixing the day of a far run-mode date keeps its year")
o.entry = [1969, 7, 20]
o.act({"do": "go"})
wait(o, 5)
check(st(o)["date"] == "20 Jul 1969" and st(o)["editing"] is None, "GO jumps to the typed date")
check(st(o)["trip"] == server.PICKED, "after GO the Pick a date row is the one lit")
o.act({"do": "edit", "field": 2})
check(st(o)["entry"] == [1969, 7, 20], "Pick a date opens on the date it last went to")
o.act({"do": "cancel"})
o.act({"do": "speed", "ypm": 2, "apply": True})
wait(o, 60)                                          # two years on
o.act({"do": "edit", "field": 2})
check(st(o)["entry"] == st(o)["ymd"] and st(o)["entry"][0] == 1971 and not st(o)["running"], f"Pick a date while running: paused, opens on the date Run reached ({st(o)['entry']})")
o.act({"do": "cancel"})
wait(o, 5)
o.act({"do": "travel", "n": 0})                      # 79 AD
wait(o, 5)
o.act({"do": "edit", "field": 2})
check(st(o)["entry"] == [79, 8, 24], f"Pick a date opens on the moment's date, 24 Aug 79 AD ({st(o)['entry']})")
o.act({"do": "nudge", "field": 0, "n": 1}); o.act({"do": "go"}); wait(o, 5)
check(st(o)["date"] == "25 Aug 79 AD" and st(o)["trip"] == server.PICKED, f"GO from it: 25 Aug 79 AD ({st(o)['date']})")
o.act({"do": "travel", "n": 1}); wait(o, 5)
o.act({"do": "edit", "field": 2})
check(st(o)["entry"] == [1776, 7, 4], f"and from the Declaration, 4 Jul 1776 ({st(o)['entry']})")
o.act({"do": "cancel"})

# ---- TIME TRAVEL ----------------------------------------------------------------
o = fresh()
want = ["24 Aug 79 AD", "4 Jul 1776", "20 Jul 1969", None]
check(len(server.EVENTS) == len(want), "four moments")
check(server.PICKED == len(server.EVENTS), "Pick a date's row comes right after the moments")
for k, text in enumerate(want):
    o.act({"do": "travel", "n": k})
    s = st(o)
    check(s["trip"] == k and s["moving"], f"travel {k}: sent there, arms moving")
    if text:
        check(s["date"] == text, f"travel {k}: date {s['date']!r}, want {text!r}")
    check(not s["deep"], f"travel {k}: no deep time")
    wait(o, 5)
o.act({"do": "travel", "n": 3})
wait(o, 5)
check(st(o)["ymd"] == [date.today().year, date.today().month, date.today().day], "Today goes to today")
o.act({"do": "travel", "n": 0})                      # 24 Aug 79 AD
wait(o, 5)
o.act({"do": "press"})
check(st(o)["running"] and st(o)["trip"] is None, "Run from 79 AD works and clears the highlight")
o.act({"do": "speed", "ypm": 2, "apply": True})
wait(o, 60)                                          # a minute at 2 years a minute
check(st(o)["ymd"][0] == 81, f"two years later it is 81 AD ({st(o)['date']})")
o.act({"do": "press"})
o.act({"do": "tab", "mode": "travel"})
o.act({"do": "turn", "n": 1})
check(st(o)["trip"] == 0, "knob turn on TIME TRAVEL goes to the next moment (from none: the first)")

# ---- tabs ------------------------------------------------------------------------
o = fresh()
check(st(o)["planet"] == 7, "PLANETS starts on Saturn (page 7: the asteroid belt is page 5)")
o.act({"do": "tab", "mode": "planets"})
o.act({"do": "planet", "n": 2})
o.act({"do": "tab", "mode": "planets"})
check(st(o)["planet"] == 2, "tapping PLANETS again keeps the page")
o.act({"do": "tab", "mode": "run"})
o.act({"do": "tab", "mode": "planets"})
check(st(o)["planet"] == 7, "coming back to PLANETS opens Saturn")
o.act({"do": "planet", "n": 5})
check(st(o)["planet"] == 5, "the asteroid belt's page")
o.act({"do": "planet", "n": 11})
check(st(o)["planet"] == 0, "eleven pages")
o.act({"do": "tab", "mode": "system"})
check(st(o)["mode"] == "run", "the old SOLAR SYSTEM tab is RUN now")
o.act({"do": "tab", "mode": "planets"})
o.act({"do": "planet", "n": 4})
check(st(o)["planet"] == 4, "a SOLAR SYSTEM tap (tab, then planet) opens that planet")
o.act({"do": "tab", "mode": "scale"})
check(st(o)["mode"] == "scale", "the scale tab")
o.act({"do": "tab", "mode": "galaxy"})
check(st(o)["mode"] == "galaxy", "the galaxy tab")
o.act({"do": "tab", "mode": "health"})
check(st(o)["mode"] == "health", "the health tab")
h = o.health()
check(h["dry_run"] and len(h["servos"]) == 8 and "cpu_c" in h["pi"] and h["running"] is False, "health report without servos")
o.act({"do": "tab", "mode": "nonsense"})
check(st(o)["mode"] == "run", "an unknown tab falls back to RUN")

# ---- circular orbits and "racing" --------------------------------------------------
o = fresh()
start = st(o)["lon"]
o.act({"do": "speed", "ypm": 5, "apply": True})
wait(o, 12)                                          # 12 s at 5 yr/min = 1 year
s = st(o)
days = 5 * 365.25 / 60 * 12
for b in range(9):
    target = (start[b] + server.MEAN_DEG_PER_DAY[b] * days) % 360
    check(abs(shortest_turn(target, s["lon"][b])) < 1, f"circular orbit {b}: {s['lon'][b]} vs {target:.2f}")
check(s["racing"] == [False] * 9, "nothing racing at 5 years a minute")
o.act({"do": "speed", "ypm": 100, "apply": True})
wait(o, 1)
racing = st(o)["racing"]
check(racing[0] and racing[3] and not racing[8], f"100 yr/min: Mercury and Mars racing, Pluto not ({racing})")
o.act({"do": "press"})
wait(o, 2)
check(st(o)["racing"] == [False] * 9, "racing clears on pause")

# Racing arms keep their order (14 Nov 2026): each planet's cap is RACE_STEP_PCT % of
# the one inside it, so the arms go Mercury > Venus > Earth > Mars ... at every speed.
class FakeArms:
    def __init__(self):
        self.rates = None
    def follow(self, lon, rate):
        self.rates = rate
    def __getattr__(self, name):       # ramp_down, stop, aim, manual: nothing to do
        return lambda *a, **k: True
o = fresh()
o.arms = FakeArms()
for ypm in server.STEPS[1:]:
    o.act({"do": "speed", "ypm": ypm, "apply": True})
    if not o.running():               # (no st(o): state() reads the real arms' details)
        o.act({"do": "press"})
    wait(o, 1)
    rpm = [r / 6 for r in o.arms.rates]
    check(all(a > b for a, b in zip(rpm, rpm[1:])), f"{ypm} yr/min: arms slower planet by planet ({[round(r, 1) for r in rpm]})")
    check(all(r <= server.cap_rpm(b) + 1e-9 for b, r in enumerate(rpm)), f"{ypm} yr/min: no arm past its cap")
check(abs(rpm[0] - server.CAP_RPM) < 1e-9 and rpm[1] < server.CAP_RPM and rpm[3] < rpm[2] < rpm[1],
      f"100 yr/min: Mercury at the cap, Venus/Earth/Mars each slower ({[round(r, 1) for r in rpm[:4]]})")

print("server rules: checks done")


# ---- the website's copy (sim.js) gives the same screen ----------------------------
SCRIPT = [
    ["wait", 5], ["act", {"do": "speed", "ypm": 50}], ["act", {"do": "speed", "ypm": 50, "apply": True}], ["wait", 2],
    ["act", {"do": "speed", "ypm": 50, "apply": True}], ["wait", 1], ["act", {"do": "speed", "ypm": 0, "apply": True}],
    ["wait", 1], ["act", {"do": "turn", "n": 1}], ["act", {"do": "press"}], ["wait", 1.5], ["act", {"do": "turn", "n": -1}],
    ["act", {"do": "press"}], ["wait", 1], ["act", {"do": "press"}], ["wait", 5],
    ["act", {"do": "tab", "mode": "planets"}], ["act", {"do": "planet", "n": 2}], ["act", {"do": "tab", "mode": "run"}],
    ["act", {"do": "tab", "mode": "planets"}], ["act", {"do": "tab", "mode": "travel"}], ["act", {"do": "tab", "mode": "health"}], ["act", {"do": "tab", "mode": "galaxy"}], ["act", {"do": "tab", "mode": "scale"}],
] + [x for k in range(4) for x in (["act", {"do": "travel", "n": k}], ["wait", 5], ["act", {"do": "press"}], ["wait", 1])] + [
    ["act", {"do": "press"}], ["wait", 5], ["act", {"do": "turn", "n": 1}], ["wait", 5],
    ["act", {"do": "today"}], ["wait", 5], ["act", {"do": "tab", "mode": "travel"}], ["act", {"do": "edit", "field": 1}], ["act", {"do": "nudge", "field": 1, "n": 3}],
    ["act", {"do": "nudge", "field": 2, "n": -30}], ["act", {"do": "go"}], ["wait", 5], ["act", {"do": "hold"}], ["wait", 5],
    ["act", {"do": "travel", "n": 0}], ["wait", 5], ["act", {"do": "edit", "field": 0}], ["act", {"do": "nudge", "field": 0, "n": 400}],
    ["act", {"do": "nudge", "field": 2, "n": -100}], ["act", {"do": "nudge", "field": 1, "n": -7}], ["act", {"do": "go"}], ["wait", 5],
    ["act", {"do": "travel", "n": 1}], ["wait", 5], ["act", {"do": "edit", "field": 2}], ["act", {"do": "nudge", "field": 2, "n": 300}], ["act", {"do": "go"}], ["wait", 5],
    ["act", {"do": "press"}], ["wait", 2], ["act", {"do": "poweroff"}], ["wait", 2],
    ["act", {"do": "mpick", "p": 0}], ["act", {"do": "mspeed", "rpm": 4.2}], ["act", {"do": "mdir", "dir": -1}],
    ["act", {"do": "mpick", "p": 9}], ["act", {"do": "mstop"}], ["act", {"do": "mpick", "all": True}],
    ["act", {"do": "manual", "on": False}], ["act", {"do": "mspeed", "rpm": 10}], ["act", {"do": "mpick", "p": 2}],
    ["act", {"do": "manual", "on": True}], ["act", {"do": "mspeed", "rpm": 40}],
    ["act", {"do": "manual", "on": False}], ["act", {"do": "lineup", "on": True}], ["wait", 3], ["act", {"do": "press"}],
    ["act", {"do": "manual", "on": True}], ["act", {"do": "tab", "mode": "travel"}], ["wait", 1],
    ["wait", 8], ["act", {"do": "lineup", "on": True}], ["act", {"do": "travel", "n": 1}], ["wait", 5],
    ["act", {"do": "lineup", "on": True}], ["act", {"do": "speed", "ypm": 5, "apply": True}], ["wait", 8],
    ["act", {"do": "lineup", "on": False}], ["act", {"do": "mnudge", "deg": 1}], ["act", {"do": "home"}], ["act", {"do": "unhome"}],
]
KEYS = ["mode", "planet", "running", "paused", "years_per_min", "ypm_set", "date", "ymd", "trip", "deep",
        "editing", "entry", "moving", "racing", "off", "manual", "man", "servo_names", "lined_up"]

NODE_SIDE = r"""
let T = 0; global.performance = { now: () => T * 1000 }; global.window = {}; global.setInterval = () => 0; global.setTimeout = () => 0; global.location = { search:'' };
eval(require('fs').readFileSync(process.argv[1], 'utf8'));
const S = window.orrerySim, out = [];
for (const [what, arg] of JSON.parse(require('fs').readFileSync(0, 'utf8'))) {
  if (what === 'wait') T += arg; else S.act(arg);
  out.push(S.state());
}
console.log(JSON.stringify(out));
"""


def python_side():
    NOW[0] = 0.0
    o = server.Orrery(None)
    out = []
    for what, arg in SCRIPT:
        if what == "wait":
            wait(o, arg)
        else:
            o.act(arg)
        out.append(o.state())
    return out


# ---- Manual mode (settings screen, 8 Nov 2026) -----------------------------------
class FakeArms:
    """Records what the motion loop asks of the servos."""
    def __init__(self):
        n = server.NUM_SERVOS
        self.ok, self.wheel, self.limp = [True] * n, [False] * n, [True] * n
        self.err_deg, self.cmd, self.live, self.hold, self.calls = [0.0] * n, [0] * n, [None] * n, True, []
    def manual(self, spin): self.calls.append(("manual", list(spin)))
    def aim(self, lon, hold_deg=None): self.calls.append(("aim", hold_deg)); self.lon = list(lon)
    def nudge(self, p, delta): self.calls.append(("nudge", p, delta))
    def release(self): self.calls.append(("release",))
    def reading(self, p): return 1234 + p
    def park(self): self.calls.append(("park",))
    def follow(self, lon, rate): self.calls.append(("follow",))
    def stop(self): self.calls.append(("stop",))
    def ramp_down(self): self.calls.append(("ramp_down",)); return True
    def rescan(self): return []


check(server.NUM_SERVOS == 8, "eight servos: built without Pluto")
NOW[0] += 100
o = server.Orrery(FakeArms())
fa = o.arms
wait(o, 5)
check(not st(o)["manual"] and ("aim", rig.START_HOLD_DEG) in fa.calls, "AUTO at start-up: arms go to the saved date (leaving ones nearly there alone)")
o.act({"do": "manual", "on": True}); wait(o, 0.3)
check(not fa.hold, "MANUAL: servos found later stay limp")
fa.calls.clear()
o.act({"do": "press"}); wait(o, 2)                  # Run on screen: the date moves, the motors do not
moved = [c for c in fa.calls if c[0] != "manual" or any(c[1])]
check(st(o)["manual"] and not moved, f"manual (and Run): no servo told to move ({moved[:3]})")
check(st(o)["running"], "manual: the screen still runs the date")
o.act({"do": "mpick", "p": 0}); o.act({"do": "mspeed", "rpm": 3}); wait(o, 0.2)
sps = round(3 * 4096 / 60)
check(fa.calls[-1] == ("manual", [sps] + [0] * 7), f"manual: Mercury alone at 3 rpm ({fa.calls[-1]})")
o.act({"do": "mdir", "dir": -1}); wait(o, 0.1)
check(fa.calls[-1][1][0] == -sps, "manual: reverse")
o.act({"do": "mstop"}); wait(o, 0.1)
check(not any(fa.calls[-1][1]) and st(o)["man"]["sel"][0], "STOP: speed 0, Mercury still picked")
o.act({"do": "mspeed", "rpm": 7}); check(st(o)["man"]["rpm"] == 5, "rpm snaps to the nearest tick")
fa.calls.clear()
o.act({"do": "manual", "on": False}); wait(o, 0.3)
names = [c[0] for c in fa.calls if c[0] != "release"]
check(names[:2] == ["ramp_down", "follow"] and "manual" not in names and fa.hold, f"AUTO: manual spin stopped, then the date drives the arms ({names[:4]})")
o.act({"do": "mspeed", "rpm": 10}); o.act({"do": "mpick", "p": 3})
check(st(o)["man"]["rpm"] == 0 and not st(o)["man"]["sel"][3], "AUTO: manual controls ignored")
o.act({"do": "press"}); wait(o, 0.5)                # pause: arms settle on the date
check(("aim", rig.AIM_HOLD_DEG) in fa.calls, "AUTO paused: arms settle on the date")
fa.calls.clear()
o.act({"do": "manual", "on": True}); wait(o, 0.3)
check(fa.calls and all(c == ("release",) or c[0] == "manual" and not any(c[1]) for c in fa.calls) and not fa.hold,
      f"back to MANUAL: arms released, nothing else ({fa.calls[:3]})")
# Opening TIME MACHINE in MANUAL switches to AUTO (14 Nov 2026): the arms go to the date.
fa.calls.clear()
o.act({"do": "tab", "mode": "travel"}); wait(o, 0.5)
check(not st(o)["manual"] and fa.hold and any(c[0] == "aim" for c in fa.calls), f"TIME MACHINE from MANUAL: AUTO, arms to the date ({[c[0] for c in fa.calls][:4]})")
o.act({"do": "tab", "mode": "health"}); o.act({"do": "manual", "on": True}); wait(o, 0.3)
fa.calls.clear()
o.act({"do": "tab", "mode": "run"}); wait(o, 0.5)
check(not st(o)["manual"] and fa.hold and any(c[0] == "aim" for c in fa.calls), "ORBITS from MANUAL: AUTO, arms to the date")
o.act({"do": "tab", "mode": "health"}); o.act({"do": "manual", "on": True}); wait(o, 0.3)
o.act({"do": "tab", "mode": "planets"}); o.act({"do": "tab", "mode": "galaxy"}); o.act({"do": "tab", "mode": "scale"}); wait(o, 0.3)
check(st(o)["manual"], "PLANETS, GALAXY and SCALE leave MANUAL on")
o.act({"do": "tab", "mode": "health"})
fa.calls.clear()
o.act({"do": "manual", "on": False}); wait(o, 0.5)
fa.calls.clear()
o.park()
wait(o, 1)
check(fa.calls == [("park",)], f"stopping (SIGTERM): arms parked, then the loop leaves them alone ({fa.calls[:3]})")

# ---- LINE UP and SAVE HOME (8 Nov 2026) ----
o = server.Orrery(FakeArms()); fa = o.arms; wait(o, 5)
o.act({"do": "press"}); wait(o, 1)
fa.calls.clear()
o.act({"do": "lineup", "on": True}); wait(o, 1)
check(st(o)["lined_up"] and not st(o)["running"] and st(o)["moving"], "LINE UP: paused, arms moving")
check(fa.lon[:8] == [rig.HOME_LON] * 8 and ("aim", rig.AIM_HOLD_DEG) in fa.calls, "LINE UP: every arm aimed at the line, forward only")
check(rig.HOME_LON == 90 and st(o)["lon"][:8] == [90.0] * 8, "travel mode: away from the screen, and the picture shows the row")
check(rig.load_home() is True, "LINE UP is saved (so a restart keeps the arms there)")
o.act({"do": "manual", "on": True}); o.act({"do": "mpick", "p": 3}); fa.calls.clear()
o.act({"do": "mnudge", "deg": 1}); o.act({"do": "mdir", "dir": -1}); o.act({"do": "mnudge", "deg": 10})
check([c for c in fa.calls if c[0] == "nudge"] == [("nudge", 3, 11), ("nudge", 3, -114)], f"manual: Mars stepped 1 deg on, 10 deg back ({fa.calls})")
o.act({"do": "mspeed", "rpm": 3}); fa.calls.clear(); o.act({"do": "mnudge", "deg": 1})
check(not [c for c in fa.calls if c[0] == "nudge"], "manual: no stepping while spinning")
o.act({"do": "mstop"}); o.act({"do": "home"})
check(rig.HOME_STEPS[3] == 1237 and st(o)["home_set"][3] and "Mars" in st(o)["note"], "SAVE HOME: Mars's reading saved")
check(abs(rig.ARM_ZERO_DEG[3] - (rig.HOME_LON - rig.ARM_DIR * 1237 * 360 / 4096) % 360) < 1e-9, "SAVE HOME: Mars's zero worked out")
rig.HOME_STEPS[3] = None; rig.load_home()
check(rig.HOME_STEPS[3] == 1237, "SAVE HOME is kept in the file")
o.act({"do": "unhome"})
check(rig.HOME_STEPS[3] is None and rig.ARM_ZERO_DEG[3] == 0 and not st(o)["home_set"][3] and "Mars" in st(o)["note"], "RESET HOME: Mars back to the built-in home")
rig.HOME_STEPS[3] = 1237; rig.load_home()
check(rig.HOME_STEPS[3] is None, "RESET HOME is kept in the file")
o.act({"do": "unhome"})
check("Nothing" in st(o)["note"], "RESET HOME with no saved home picked: says so")
o.act({"do": "home"})
o.act({"do": "manual", "on": False}); wait(o, 1)
check(fa.lon[:8] == [rig.HOME_LON] * 8, "back to AUTO, still lined up: arms go back to the line")
o.act({"do": "press"}); wait(o, 1)
check(not st(o)["lined_up"] and not st(o)["running"] and fa.lon[0] != rig.HOME_LON, "Run while lined up: arms go back to the date first, Run not started")
o.act({"do": "lineup", "on": True}); wait(o, 1); o.act({"do": "travel", "n": 2}); wait(o, 1)
check(not st(o)["lined_up"] and st(o)["trip"] == 2, "TIME TRAVEL while lined up: goes to the moment")
check(rig.load_home() is False, "leaving the line is saved too")
rig.HOME_STEPS[:] = [None] * 8; rig.zero_from_home()
NOW[0] = 1000.0


node = shutil.which("node")
if not node:
    print("sim.js vs server: skipped (no node here)")
else:
    sim = subprocess.run([node, "-e", NODE_SIDE, str(Path(__file__).parent / "ui" / "sim.js")],
                         input=json.dumps(SCRIPT), capture_output=True, text=True)
    if sim.returncode:
        check(False, "sim.js did not run: " + sim.stderr[-300:])
    else:
        mine, theirs = python_side(), json.loads(sim.stdout)
        for i, (a, b) in enumerate(zip(mine, theirs)):
            for k in KEYS:
                if k == "racing" and SCRIPT[i][0] != "wait":
                    continue                 # the server works this out on its next 0.1 s tick
                if a[k] != b[k]:
                    check(False, f"sim.js step {i} {SCRIPT[i]}: {k} server {a[k]!r} vs sim {b[k]!r}")
            for p in range(9):
                if abs(shortest_turn(a["lon"][p], b["lon"][p])) > 0.3:
                    check(False, f"sim.js step {i}: planet {p} at {a['lon'][p]} vs {b['lon'][p]}")
        print(f"sim.js vs server: {len(SCRIPT)} steps compared")

print("all checks passed" if not failures else f"{failures} FAILED")
raise SystemExit(1 if failures else 0)
