#!/usr/bin/env python3
"""planet dial -- turn a knob, pick a date, the planets swing to where they really are.

Runs on the Raspberry Pi inside the box. Also runs on a laptop with just the
servo driver board plugged into USB, which is how to test before the knob and
screen are wired:

    python3 orrery.py --keys            # no knob/LCD: type commands instead
    python3 orrery.py --keys --dry-run  # no servos either: just print the angles

Knob:  turn = change the date      short press = change step (day/week/month/year)
       long press = back to today

FIRST RUN: every servo leaves the factory as ID 1. Number them 1..9 one at a
time with servo_tool.py before they share a bus.
"""

import argparse
import calendar
import json
import math
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from planets import BODY_NAMES, J2000, NUM_BODIES, longitudes, planet_longitude, shortest_turn

# ---- Settings ---------------------------------------------------------------

# Planet p is servo ID p+1: Mercury 1 ... Neptune 8. (0 and 254 are broadcast.)
# Built without Pluto (7 Nov 2026): eight servos, never a ninth. The maths still has
# Pluto (planets.py: the screen's 3D views and facts); it simply has no arm.
SERVO_ID = [1, 2, 3, 4, 5, 6, 7, 8]
NUM_SERVOS = len(SERVO_ID)

STEPS_PER_TURN = 4096                 # 0.088 deg per step
STEP_LIMIT = 7 * STEPS_PER_TURN       # multi-turn counter runs out a little past +/-7 turns
SERVO_SPEED = 600                     # steps/s, about 0.15 turn/s (8.8 rpm): every go-to-a-date move
                                      # (TIME TRAVEL, GO, Today, settle after pause). 7 Nov 2026: cut 75 %
                                      # from 2400 so the gears don't slip (user); admin max 600
SERVO_ACC = 30                        # 0 = jump straight there
# Torque cap, 0..1000 = 0..100 %. On the STS3215 this caps motor power, so it also
# caps top speed: measured 25 Sep 2026 (no load, 7.3 V) 15 % = ~7.5 rpm, 50 % = 20 rpm,
# 40 rpm used ~75 %, flat out ~50 rpm at ~94 %. 80 % lets Mercury reach 40 rpm and
# SERVO_SPEED be met; a foam ball on a wire arm still can't pinch much.
SERVO_TORQUE_LIMIT = 800
# Direction. Planets orbit counter-clockwise seen from above (ecliptic north), and
# longitude grows that way. An STS3215 turns CLOCKWISE (seen from its horn) for
# increasing steps (checked 25 Sep 2026), and the servo gear -> tube gear mesh
# reverses it, so +steps = arm counter-clockwise = correct. Bare servos on the bench
# (no gears) therefore turn clockwise, backwards to the sky; that is expected.
ARM_DIR = 1                           # -1 only if the arms end up running backwards

# Arms only ever turn FORWARD, the planets' own direction (user, 7 Nov 2026): jumps to a
# date (TIME TRAVEL, GO, Today, start-up), the settle onto the exact date when Run is
# paused, and Run's own catch-up corrections. Even when forward is the long way round:
# Run moves the planets on circles, so on pause Mercury can stand up to ~24 deg past its
# true place and then goes on nearly a full turn (~7 s at SERVO_SPEED). Never backwards,
# not even a nudge: a target no more than AIM_HOLD_DEG behind an arm is close enough, and
# the arm stays put (a whole lap for a hair was what moved the arms at a restart, 7 Nov).
# At start-up the arms may stand where a Run was cut short (the saved date's true place
# can be up to ~24 deg behind them): within START_HOLD_DEG they stay put too, and catch up
# on the next move or Run.
AIM_HOLD_DEG = 2
START_HOLD_DEG = 30

# Run mode. The date advances at a steady rate, set as Mercury's turns per minute
# (the fastest arm); every arm follows its planet's true angle for that date.
# Constant-speed (wheel) mode cannot go below 50 steps/s -- anything slower comes out
# at exactly 50 (measured 25 Sep) -- so fast arms run in wheel mode, steered to stay on
# their angle, and slow arms are stepped along in position mode.
MERCURY_DAYS = 87.969
RUN_RPM_MAX = 40                      # measured no-load top speed ~50 rpm; keep a margin
WHEEL_ON, WHEEL_OFF = 100, 70         # steps/s: hysteresis for switching an arm's mode
WHEEL_KP = 6.0                        # steps/s of correction per step of angle error
                                      # (2.0 let Mercury lag 7 deg at 20 rpm, 25 Sep)
RUN_TICK = 0.1                        # s
# Ramps: wheel-mode speed changes by at most this much per tick, so 40 rpm <-> stop
# takes ~1.1 s. Done in software because the servo's own ACC register gave
# inconsistent stops (measured 25 Sep); gentler on the plastic gears and the arms.
WHEEL_SLEW = 250                      # steps/s per RUN_TICK (= 2500 steps/s^2)
WHEEL_FIX_MAX = 300                   # steps/s: most a spinning arm speeds up/slows to catch up

# Where each arm points when its servo reads 0 steps (an ecliptic longitude). Worked
# out from the line-up calibration below (zero_from_home); 0 for an arm not calibrated.
ARM_ZERO_DEG = [0.0] * NUM_SERVOS

# Travel mode / home position (8 Nov 2026 as LINE UP, the user's design; 13 Nov 2026 renamed
# TRAVEL MODE and turned round). Every arm points the same way, AWAY from the screen (to the
# back of the box), all the planets in one row. It is where the model goes before it is
# carried (settings: TRAVEL MODE), the position the arms are clamped on in (a servo with no
# saved home goes to the step that stands for HOME_LON, and the arm is clamped pointing
# away from the screen: calibrated by construction), and the check: in travel mode every
# planet should sit on one straight line. HOME_LON is the longitude that direction stands
# for: 90 deg, the top of the screen's 3D view at its starting angle (longitude 270 at the
# bottom of the picture, towards the viewer; 0 to the right), so the model, seen from the
# screen, matches the picture on it. (Until 13 Nov 2026 the line pointed out over the
# screen, 270; a home saved then is turned half a turn when it is read, load_home.) The servo and tube gears are both 40T, so one servo
# turn is one arm turn and the servo's 0..4095 reading tells where its arm points, even
# after a power cut. HOME_STEPS[p] is that reading with planet p's arm on the line (saved
# from the settings screen in MANUAL: step the arm onto the line, SAVE HOME); None = not
# yet calibrated.
HOME_LON = 90.0
HOME_STEPS = [None] * NUM_SERVOS
HOME_FILE = Path.home() / ".orrery_home.json"
NUDGE_SPEED = 200                     # steps/s: MANUAL's 1 deg / 10 deg steps, gently


def zero_from_home():
    """ARM_ZERO_DEG from HOME_STEPS: an arm at step s points at ARM_ZERO_DEG + ARM_DIR x s
    (in degrees), and at HOME_STEPS it points at HOME_LON."""
    for p in range(NUM_SERVOS):
        h = HOME_STEPS[p]
        ARM_ZERO_DEG[p] = 0.0 if h is None else (HOME_LON - ARM_DIR * h * 360.0 / STEPS_PER_TURN) % 360.0


def home_step(p):
    """The servo reading (0..4095) that puts planet p's arm on the line: the saved one, or
    for an arm with no saved home the one ARM_ZERO_DEG stands for."""
    h = HOME_STEPS[p]
    if h is None:
        h = round((HOME_LON - ARM_ZERO_DEG[p]) * ARM_DIR * STEPS_PER_TURN / 360.0)
    return h % STEPS_PER_TURN


def from_line(p, position):
    """How far planet p's arm is from the travel-mode line, -180..180 deg (+ = ahead,
    the planets' way), from a servo reading."""
    if position is None:
        return None
    h = home_step(p)
    return ((position - h) * ARM_DIR * 360.0 / STEPS_PER_TURN + 180.0) % 360.0 - 180.0


def load_home():
    """Read the calibration (and whether the arms were left lined up). Returns lined_up."""
    try:
        d = json.loads(HOME_FILE.read_text())
        steps = d.get("home_steps", [])
        # Saved when the line pointed another way (270 until 13 Nov 2026): turn it round.
        turn = round((HOME_LON - float(d.get("home_lon", HOME_LON))) * ARM_DIR * STEPS_PER_TURN / 360.0)
        for p in range(NUM_SERVOS):
            h = steps[p] if p < len(steps) else None
            HOME_STEPS[p] = None if h is None else (int(h) + turn) % STEPS_PER_TURN
        lined_up = bool(d.get("lined_up"))
    except (OSError, ValueError, TypeError, AttributeError):
        lined_up = False
    zero_from_home()
    return lined_up


def save_home(lined_up):
    try:
        HOME_FILE.write_text(json.dumps({"home_steps": HOME_STEPS, "lined_up": bool(lined_up),
                                         "home_lon": HOME_LON}, indent=1))
    except OSError:
        pass

# Pi header, BCM numbering. The KY-040's "+" pin goes to 3.3 V, NOT 5 V: the
# Pi's inputs are not 5 V tolerant.
PIN_ENC_CLK, PIN_ENC_DT, PIN_ENC_SW = 17, 27, 22
LCD_ADDRESS = 0x27                    # try 0x3F if the screen stays blank

DAY_MIN = date(1800, 1, 1)            # JPL Table 1 is fitted for 1800-2050 (used to 2100);
DAY_MAX = date(2200, 12, 31)          # Table 2 (~1 deg) past that: 2200 takes in the 2149 line-up

STATE_FILE = Path.home() / ".planet_dial.json"
STEP_NAMES = ["1 day", "1 week", "1 month", "1 year"]


# ---- Date dial (pure logic, no hardware) ------------------------------------

class Dial:
    def __init__(self, day):
        self.step = 0
        self.set(day)

    def set(self, day, keep_wanted_day=False):
        self.day = min(max(day, DAY_MIN), DAY_MAX)
        if not keep_wanted_day:
            # so 31 Jan + 1 month + 1 month lands on 31 Mar, not 28 Mar
            self.wanted_dom = self.day.day

    def turn(self, clicks):
        if self.step == 0:
            return self.set(self.day + timedelta(days=clicks))
        if self.step == 1:
            return self.set(self.day + timedelta(weeks=clicks))
        months = self.day.year * 12 + self.day.month - 1 + clicks * (12 if self.step == 3 else 1)
        y, m = divmod(months, 12)
        y = min(max(y, DAY_MIN.year - 1), DAY_MAX.year + 1)   # set() does the exact clamp
        d = min(self.wanted_dom, calendar.monthrange(y, m + 1)[1])
        self.set(date(y, m + 1, d), keep_wanted_day=True)

    def next_step(self):
        self.step = (self.step + 1) % len(STEP_NAMES)


def steps_for_angle(deg, zero_deg, current_steps, hold_deg=None):
    """The step count that points an arm at `deg`. With hold_deg=None it picks the
    one nearest to where the arm already is, so it takes the short way round. With
    hold_deg it goes forward only (the planet's own direction) to the first such
    count; a target no more than hold_deg behind gives current_steps (stay put). Then
    it pulls it back inside the counter's range if that would overflow. Dropping a
    whole turn leaves the arm pointing the same way, that one move just goes the long way."""
    T = STEPS_PER_TURN
    base = round(((deg - zero_deg) * ARM_DIR) % 360.0 * T / 360.0)
    if hold_deg is None:
        want = base + round((current_steps - base) / T) * T
    else:
        s = 1 if ARM_DIR > 0 else -1           # forward = more steps when ARM_DIR = 1
        ahead = (s * (base - current_steps)) % T     # forward steps to the target, 0..T-1
        if ahead and T - ahead <= hold_deg * T / 360.0:
            return current_steps               # just behind: close enough, never back
        want = current_steps + s * ahead
    while want > STEP_LIMIT:
        want -= STEPS_PER_TURN
    while want < -STEP_LIMIT:
        want += STEPS_PER_TURN
    return want


# ---- Hardware ---------------------------------------------------------------

def find_port():
    from serial.tools import list_ports
    ports = [p.device for p in list_ports.comports()
             if any(k in p.device for k in ("ttyUSB", "ttyACM", "usbmodem", "usbserial"))]
    if not ports:
        sys.exit("No USB serial port found. Is the servo driver board plugged in?")
    return ports[0]


class Arms:
    """Unlike steppers, these servos know where they are. Read each one at
    power-on and the model is already correct -- no homing needed.

    hold=False (manual mode, 8 Nov 2026): servos are found but left limp (torque
    off), so nothing moves at start-up and the gears turn by hand. The next aim() or
    follow() switches a limp servo back on (via _reanchor)."""

    def __init__(self, bus, hold=True):
        self.bus = bus
        self.hold = hold                   # attach with torque on (auto) or limp (manual)
        self.ok = [False] * NUM_SERVOS
        self.steps = [0] * NUM_SERVOS      # the servo's own multi-turn count, as we track it
        self.wheel = [False] * NUM_SERVOS
        self.limp = [False] * NUM_SERVOS   # torque off: turns freely by hand
        self.err_deg = [0.0] * NUM_SERVOS  # Run mode: how far each arm is off its planet
        self.cmd = [0] * NUM_SERVOS        # last wheel speed sent, for the ramps
        self.live = [None] * NUM_SERVOS    # each servo's latest snapshot() (feetech.py), read every Run tick
        self.held = [False] * NUM_SERVOS   # manual: stepped with nudge(), so holding (not limp) until STOP
        for p, sid in enumerate(SERVO_ID):
            if self._attach(p):
                print(f"{BODY_NAMES[p]:8} ok id {sid} at step {self.steps[p]}")
            else:
                print(f"{BODY_NAMES[p]:8} NO REPLY id {sid}")

    def _attach(self, p):
        sid = SERVO_ID[p]
        if not self.bus.ping(sid):
            return False
        if not self.hold:
            self.bus.enable_torque(sid, False)   # manual: limp first, before any mode change
        self.bus.ensure_multi_turn(sid)
        self.bus.set_torque_limit(sid, SERVO_TORQUE_LIMIT)
        if self.hold:
            self._reanchor(p)
        else:
            self._go_limp(p)
        self.ok[p] = True
        return True

    def _go_limp(self, p):
        """Torque off: the motor stops pushing and the gear turns freely by hand."""
        sid = SERVO_ID[p]
        if self.wheel[p]:
            self.bus.set_speed(sid, 0, 0)
        self.bus.enable_torque(sid, False)
        self.steps[p] = self.bus.position(sid)
        self.wheel[p] = False
        self.limp[p] = True
        self.cmd[p] = 0

    def _lost(self, p, e):
        """A servo stopped answering (26 Sep: the 7.4 V supply cut out as Run started).
        Forget it; rescan() re-attaches it when it answers again - that also switches
        its torque back on, which a power cut turns off - instead of every later
        command failing while the program believes it is still fine."""
        print(f"{BODY_NAMES[p]} (id {SERVO_ID[p]}) lost: {e}", flush=True)
        self.ok[p] = self.wheel[p] = self.limp[p] = self.held[p] = False
        self.cmd[p] = 0

    def rescan(self):
        """Pick up servos that were unpowered at start-up (or plugged in later).
        Returns the planets that just appeared; the caller should aim them."""
        return [p for p in range(NUM_SERVOS) if not self.ok[p] and self._attach(p)]

    def _reanchor(self, p):
        """The servo counts whole turns internally, but its position register only
        reports 0..4095, so after it has turned a few times we cannot read where it
        thinks it is -- and a goal computed from the register sends it several turns
        the wrong way (25 Sep: Mercury ran away backwards). Switching it to wheel mode
        and back resets the count to the register (measured 25 Sep), so do that
        whenever the count is unknown or getting large. Costs two EEPROM writes."""
        sid = SERVO_ID[p]
        self.bus.set_speed(sid, 0, SERVO_ACC)
        # Torque off while the mode changes, then make "where it is" the goal before
        # torque comes back on. Otherwise, the moment it is in position mode again, the
        # servo heads for the goal left over from before the run, possibly behind it, at
        # full speed (the leftover goal speed is the 0 of the stopped spin, and in
        # position mode 0 means flat out) -- a backwards jerk until aim() is sent (7 Nov 2026).
        self.bus.enable_torque(sid, False)
        self.bus.set_mode(sid, 1)
        self.bus.set_mode(sid, 0)
        here = self.bus.position(sid)
        self.bus.move_to(sid, here, SERVO_SPEED, SERVO_ACC)
        self.bus.enable_torque(sid)
        self.steps[p] = here
        self.wheel[p] = self.limp[p] = False
        self.cmd[p] = 0

    def _ramp(self, p, want):
        """Send a wheel speed no more than WHEEL_SLEW away from the last one."""
        step = max(-WHEEL_SLEW, min(WHEEL_SLEW, want - self.cmd[p]))
        self.cmd[p] += step
        self.bus.set_speed(SERVO_ID[p], self.cmd[p], 0)

    def ramp_down(self):
        """One tick of slowing every spinning arm towards a stop. True once all are
        stopped (commanded 0 and reading nearly 0), so modes can safely be switched."""
        from feetech import ServoError
        done = True
        for p in range(NUM_SERVOS):
            if self.ok[p] and self.wheel[p]:
                try:
                    self._ramp(p, 0)
                    self.live[p] = self.bus.snapshot(SERVO_ID[p])
                    if self.cmd[p] != 0 or abs(self.live[p]["speed"]) > 60:
                        done = False
                except ServoError as e:
                    self._lost(p, e)             # a dead servo must not hold up the stop
        return done

    def aim(self, lon_deg, hold_deg=AIM_HOLD_DEG):
        """Send every arm to its angle, forward only; one already within `hold_deg`
        past it stays put (None = the short way, either direction)."""
        from feetech import ServoError
        for p, sid in enumerate(SERVO_ID):
            if not self.ok[p]:
                continue
            try:
                if self.wheel[p] or self.limp[p] or abs(self.steps[p]) > 4 * STEPS_PER_TURN:
                    self._reanchor(p)
                self.steps[p] = steps_for_angle(lon_deg[p], ARM_ZERO_DEG[p], self.steps[p], hold_deg)
                self.bus.move_to(sid, self.steps[p], SERVO_SPEED, SERVO_ACC)
            except ServoError as e:
                self._lost(p, e)


    def follow(self, lon_deg, rate_deg_s):
        """One Run-mode tick: keep each arm on its planet's angle while it moves at
        `rate_deg_s` (degrees per second, + = the planet's own direction).
        An angle of None means "racing": the date moves too fast for this servo, so
        it just spins at `rate` and its position is not kept (server.py)."""
        from feetech import ServoError
        for p, sid in enumerate(SERVO_ID):
            if not self.ok[p]:
                continue
            rate = rate_deg_s[p] * ARM_DIR * STEPS_PER_TURN / 360.0
            try:
                seen = self.live[p] = self.bus.snapshot(sid)   # one read: position, speed, current...
                fast = abs(rate) >= (WHEEL_OFF if self.wheel[p] else WHEEL_ON)
                if fast:
                    if not self.wheel[p]:
                        self.bus.set_mode(sid, 1)
                        self.bus.enable_torque(sid)
                        self.wheel[p], self.limp[p] = True, False
                        self.cmd[p] = seen["speed"]   # ramp from how fast it really is
                    if lon_deg[p] is None:
                        self.err_deg[p] = 0.0
                        self._ramp(p, max(-3300, min(3300, round(rate))))
                        continue
                    want = ((lon_deg[p] - ARM_ZERO_DEG[p]) * ARM_DIR) % 360.0 * STEPS_PER_TURN / 360.0
                    err = (want - seen["position"] + 2048) % 4096 - 2048
                    self.err_deg[p] = err * 360 / STEPS_PER_TURN
                    # Cap the correction: with the ramp, a big error (e.g. 115 deg) steered
                    # at full KP overshot by ~50 deg and swung back (measured 25 Sep).
                    fix = max(-WHEEL_FIX_MAX, min(WHEEL_FIX_MAX, WHEEL_KP * err))
                    # An arm ahead of its planet slows down, at most to a stop: never backwards.
                    speed = rate + fix
                    speed = max(0.0, speed) if rate > 0 else min(0.0, speed)
                    self._ramp(p, max(-3300, min(3300, round(speed))))
                else:
                    if self.wheel[p] or self.limp[p] or abs(self.steps[p]) > 5 * STEPS_PER_TURN:
                        self._reanchor(p)
                    target = steps_for_angle(lon_deg[p], ARM_ZERO_DEG[p], self.steps[p])
                    if (target - self.steps[p]) * rate < 0:
                        target = self.steps[p]       # planet behind the arm: wait for it, never back
                    self.err_deg[p] = (target - seen["position"] + 2048) % 4096 - 2048
                    self.err_deg[p] *= 360 / STEPS_PER_TURN
                    self.steps[p] = target
                    self.bus.move_to(sid, target, max(60, round(2 * abs(rate)) + 50), 0)
            except ServoError as e:
                self._lost(p, e)

    def park(self, seconds=3):
        """The program is being stopped (systemctl stop / restart / reboot): ramp any
        spinning arm down and hold every arm where it is. No settling on the date: that
        would be a move right before the Pi goes down."""
        t_end = time.monotonic() + seconds
        while not self.ramp_down() and time.monotonic() < t_end:
            time.sleep(RUN_TICK)
        from feetech import ServoError
        for p in range(NUM_SERVOS):
            if self.ok[p] and self.wheel[p]:
                try:
                    self._reanchor(p)
                except ServoError:
                    pass

    def stop(self):
        """Leave Run mode: ramp every spinning arm down, then back to position mode."""
        t_end = time.monotonic() + 4
        while not self.ramp_down() and time.monotonic() < t_end:
            time.sleep(RUN_TICK)
        from feetech import ServoError
        for p in range(NUM_SERVOS):
            if self.ok[p] and self.wheel[p]:
                try:
                    self._reanchor(p)
                except ServoError as e:
                    self._lost(p, e)

    def manual(self, spin):
        """One manual-mode tick (the settings screen, 8 Nov 2026): spin[p] = wheel
        speed in steps/s for each servo (0 = stop). A servo told to spin goes to wheel
        mode with torque on and ramps (WHEEL_SLEW) to its speed; one told to stop ramps
        down and then goes limp, so its gear can be turned by hand again."""
        from feetech import ServoError
        for p, sid in enumerate(SERVO_ID):
            if not self.ok[p]:
                continue
            want = spin[p]
            try:
                if want:
                    if not self.wheel[p]:
                        self.bus.set_mode(sid, 1)
                        self.bus.enable_torque(sid)
                        self.wheel[p], self.limp[p] = True, False
                        self.cmd[p] = 0
                    self.held[p] = False
                    self._ramp(p, want)
                    self.live[p] = self.bus.snapshot(sid)
                elif self.wheel[p]:
                    self._ramp(p, 0)
                    self.live[p] = self.bus.snapshot(sid)
                    if self.cmd[p] == 0 and abs(self.live[p]["speed"]) <= 60:
                        self._go_limp(p)
                elif not self.limp[p] and not self.held[p]:
                    self._go_limp(p)         # left holding from auto mode: let it go
            except ServoError as e:
                self._lost(p, e)

    def nudge(self, p, delta):
        """Manual mode: step one arm `delta` steps (a degree or ten) and hold it there,
        to put it exactly on the line before SAVE HOME (8 Nov 2026). Not while it spins."""
        from feetech import ServoError
        if not self.ok[p] or self.wheel[p]:
            return
        try:
            if self.limp[p] or abs(self.steps[p]) > 4 * STEPS_PER_TURN:
                self._reanchor(p)            # torque on, holding where it stands
            self.steps[p] += delta
            self.bus.move_to(SERVO_ID[p], self.steps[p], NUDGE_SPEED, SERVO_ACC)
            self.held[p] = True
        except ServoError as e:
            self._lost(p, e)

    def release(self):
        """Manual STOP (and entering or leaving MANUAL): stepped arms stop holding."""
        self.held = [False] * NUM_SERVOS

    def reading(self, p):
        """Planet p's servo reading now, 0..4095 (SAVE HOME)."""
        return self.bus.position(SERVO_ID[p]) % STEPS_PER_TURN


def run(arms, start_day, rpm, seconds=None, report=print):
    """Run mode: the date advances steadily, Mercury turning `rpm` times a minute
    (negative = backwards in time), every planet at its true relative speed and in
    its own direction. Returns the date reached. Ctrl-C or `seconds` stops it."""
    rpm = max(-RUN_RPM_MAX, min(RUN_RPM_MAX, rpm))
    days_per_s = rpm / 60.0 * MERCURY_DAYS
    day = float((start_day - J2000).days)
    if arms:
        # Line every arm up on the start date first. Without this, an arm that was
        # left somewhere else (Saturn, 57 deg off on 25 Sep) spends seconds catching up.
        arms.aim(longitudes(start_day))
        time.sleep(2.5)
    t_last = t_report = time.monotonic()
    t_end = None if seconds is None else t_last + seconds
    try:
        while True:
            now = time.monotonic()
            day += days_per_s * (now - t_last)
            t_last = now
            lon = [planet_longitude(b, day) for b in range(NUM_BODIES)]
            ahead = [planet_longitude(b, day + 0.5) for b in range(NUM_BODIES)]
            rate = [shortest_turn(a, b) / 0.5 * days_per_s for a, b in zip(lon, ahead)]
            if arms:
                arms.follow(lon, rate)
            if now - t_report >= 1.0:
                t_report = now
                off = ""
                if arms:
                    off = "  off by " + " ".join(f"{BODY_NAMES[p][:3]} {arms.err_deg[p]:+.1f}"
                                                 for p in range(NUM_SERVOS) if arms.ok[p])
                report(f"{J2000 + timedelta(days=int(day))}  Mercury {rpm:+.0f} rpm = "
                       f"{days_per_s * 60 / 365.25:.1f} years/min{off}")
            if t_end is not None and now >= t_end:
                break
            time.sleep(RUN_TICK)
    except KeyboardInterrupt:
        pass
    reached = min(max(J2000 + timedelta(days=round(day)), DAY_MIN), DAY_MAX)
    if arms:
        arms.stop()
        arms.aim(longitudes(reached))
    return reached


class Lcd:
    def __init__(self):
        from RPLCD.i2c import CharLCD
        self.lcd = CharLCD("PCF8574", LCD_ADDRESS, cols=16, rows=2)

    def show(self, dial):
        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(f"{dial.day.day:2} {dial.day:%b %Y}".center(16))
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(f"Turn = {STEP_NAMES[dial.step]:<9}")


class Knob:
    def __init__(self):
        from gpiozero import Button, RotaryEncoder
        self.clicks = 0
        self.presses = []
        self.enc = RotaryEncoder(PIN_ENC_CLK, PIN_ENC_DT, max_steps=0)
        self.btn = Button(PIN_ENC_SW, pull_up=True, hold_time=1.0, bounce_time=0.03)
        self.held = False
        self.btn.when_held = self._held
        self.btn.when_released = self._released

    def _held(self):
        self.held = True
        self.presses.append("long")

    def _released(self):
        if not self.held:
            self.presses.append("short")
        self.held = False

    def events(self):
        """-> list of ("turn", n) / ("short",) / ("long",) since the last call."""
        out = []
        n, self.enc.steps = self.enc.steps, 0
        if n:
            out.append(("turn", n))
        while self.presses:
            out.append((self.presses.pop(0),))
        return out


class Keys:
    """Stand-in for the knob: commands typed on stdin."""
    HELP = "+ / - / +5 / -12 = turn   s = step size   t = today   2027-02-20 = go to date   q = quit"

    def __init__(self):
        print(self.HELP)

    def events(self):
        try:
            line = input("> ").strip()
        except EOFError:
            return [("quit",)]
        if line == "q":
            return [("quit",)]
        if line == "s":
            return [("short",)]
        if line == "t":
            return [("long",)]
        if line in ("+", "-"):
            line += "1"
        try:
            return [("turn", int(line))]
        except ValueError:
            pass
        try:
            return [("goto", date.fromisoformat(line))]
        except ValueError:
            print(self.HELP)
            return []


# ---- Main -------------------------------------------------------------------

def load_day():
    try:
        return date.fromisoformat(json.loads(STATE_FILE.read_text())["day"])
    except (OSError, ValueError, KeyError):
        return date.today()


def save_day(day):
    try:
        STATE_FILE.write_text(json.dumps({"day": day.isoformat()}))
    except OSError:
        pass  # read-only SD card: fine, we start from today instead


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="servo driver board serial port (default: auto-detect)")
    ap.add_argument("--keys", action="store_true", help="no knob or LCD: type commands instead")
    ap.add_argument("--dry-run", action="store_true", help="no servos: just print the angles")
    ap.add_argument("--run", type=float, metavar="RPM",
                    help=f"Run mode: Mercury at RPM turns/min (max {RUN_RPM_MAX}, negative = back in time)")
    ap.add_argument("--seconds", type=float, help="with --run: stop after this long (default: Ctrl-C)")
    args = ap.parse_args()
    load_home()                           # the arms' calibration (server.py's settings screen)

    if args.run is not None:
        arms = None
        if not args.dry_run:
            from feetech import Bus
            arms = Arms(Bus(args.port or find_port()))
        reached = run(arms, load_day(), args.run, args.seconds)
        print(f"stopped at {reached}")
        save_day(reached)
        return

    arms = None
    if not args.dry_run:
        from feetech import Bus
        arms = Arms(Bus(args.port or find_port()))
    lcd = None if args.keys else Lcd()
    knob = Keys() if args.keys else Knob()

    dial = Dial(load_day())
    saved_day, last_change = dial.day, time.monotonic()

    def show(move=True):
        nonlocal last_change
        lon = longitudes(dial.day)
        if lcd:
            lcd.show(dial)
        if arms and move:
            arms.aim(lon)
        print(f"{dial.day}  [{STEP_NAMES[dial.step]}]  " +
              "  ".join(f"{n} {a:.1f}" for n, a in zip(BODY_NAMES, lon)))
        last_change = time.monotonic()

    show()
    while True:
        for ev in knob.events():
            if ev[0] == "quit":
                return
            if ev[0] == "turn":
                dial.turn(ev[1])
            elif ev[0] == "goto":
                dial.set(ev[1])
            elif ev[0] == "long":
                dial.set(date.today())
            elif ev[0] == "short":
                dial.next_step()
            show(move=ev[0] != "short")

        # Remember the date once things have been still for 5 s (spares the SD card).
        if dial.day != saved_day and time.monotonic() - last_change > 5:
            save_day(dial.day)
            saved_day = dial.day
        if not args.keys:
            time.sleep(0.02)


if __name__ == "__main__":
    main()
