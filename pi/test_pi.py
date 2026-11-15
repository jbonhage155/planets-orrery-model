#!/usr/bin/env python3
"""Desktop checks, no hardware needed:   python3 test_pi.py

1. planets.py against NASA JPL Horizons (same reference values as
   arduino/test/test_planets.cpp: observer table, centre = Sun (500@10),
   quantity 18, fetched 20 Sep 2026).
2. feetech.py against a fake servo that speaks the same packet format. This
   proves the driver is self-consistent and matches the documented protocol as
   I understand it. It proves NOTHING about a real servo.
3. The dial and the multi-turn step logic in orrery.py.
"""

from datetime import date

import feetech
import orrery
from planets import BODY_NAMES, J2000, cal_from_day, day_from_cal, planet_longitude, shortest_turn, year_text

failures = 0


def check(ok, msg):
    global failures
    if not ok:
        failures += 1
        print("FAIL:", msg)


# ---- 1. orbit maths ----------------------------------------------------------

REFS = [
    (0.0, "2000-Jan-01 12:00", [253.7776, 182.5974, 100.3728, 359.4427, 36.2920, 45.7203, 316.4174, 303.9278, 250.5451]),
    (3455.5, "2009-Jun-18 00:00", [330.0073, 318.0036, 266.7705, 12.2196, 316.8385, 171.7223, 353.5163, 324.5650, 271.8136]),
    (9759.5, "2026-Sep-21 00:00", [239.7176, 337.6092, 357.6653, 80.2830, 130.3285, 10.4590, 62.5379, 2.5868, 304.1596]),
    (17455.5, "2047-Oct-17 00:00", [30.6799, 67.2823, 22.8758, 144.9506, 47.4906, 274.1395, 156.7206, 49.3626, 335.1344]),
]
worst = 0.0
for days, label, want in REFS:
    for b, w in enumerate(want):
        err = shortest_turn(w, planet_longitude(b, days))
        worst = max(worst, abs(err))
        check(abs(err) < 0.25, f"{label} {BODY_NAMES[b]} off by {err:+.3f} deg")
print(f"orbit maths: worst error {worst:.3f} deg")
check((date(2026, 9, 21) - J2000).days == 9760, "2026-09-21 should be day 9760")

# TIME TRAVEL dates (26 Sep): JPL Table 2 against Horizons (heliocentric ecliptic
# J2000 vectors, centre 500@10, Mercury ... Neptune; dates Julian before 1582).
OLD_REFS = {
    (-6, 10, 1): [339.41, 12.85, 33.65, 307.94, 18.9, 17.23, 2.13, 242.62],
    (79, 8, 24): [199.35, 11.73, 355.22, 6.7, 79.35, 334.5, 5.52, 68.66],
    (1453, 5, 29): [161.8, 27.94, 263.91, 144.55, 5.96, 216.74, 127.95, 191.31],
    (1492, 10, 12): [294.11, 28.18, 35.61, 124.41, 126.65, 326.26, 303.96, 276.06],
    (1776, 7, 4): [271.53, 81.06, 286.05, 69.84, 97.58, 203.94, 70.34, 177.34],
}
worst = 0.0
for cal, want in OLD_REFS.items():
    for b, w in enumerate(want):
        err = shortest_turn(w, planet_longitude(b, day_from_cal(*cal)))
        worst = max(worst, abs(err))
        check(abs(err) < 0.5, f"{cal} {BODY_NAMES[b]} off by {err:+.3f} deg")
print(f"old dates (3000 BC - 1800): worst error {worst:.3f} deg")
# Calendar: round trips, the 1582 switch (4 Oct was followed by 15 Oct), BC years.
for n in (-800000, -701397, -152385, -152384, 0, 9760):
    check(day_from_cal(*cal_from_day(n)) == n, f"day {n} does not round-trip")
check(cal_from_day(day_from_cal(1582, 10, 4) + 1) == [1582, 10, 15], "Julian to Gregorian switch")
check(cal_from_day(0) == [2000, 1, 1] and day_from_cal(1969, 7, 20) == (date(1969, 7, 20) - J2000).days, "Gregorian dates")
check([year_text(y) for y in (-6, 0, 1, 79, 1066)] == ["7 BC", "1 BC", "1 AD", "79 AD", "1066"], "year text")


# ---- 2. servo driver against a fake servo ------------------------------------

class FakeServoPort:
    """One or more pretend servos on a pretend wire. `echo` mimics an adapter
    that loops TX back onto RX."""

    def __init__(self, ids, echo=False):
        self.mem = {i: bytearray(80) for i in ids}
        for i, m in self.mem.items():
            m[feetech.REG_ID] = i
            m[feetech.REG_LOCK] = 1
            m[feetech.REG_MAX_ANGLE_LIMIT:feetech.REG_MAX_ANGLE_LIMIT + 2] = (4095).to_bytes(2, "little")
        self.echo = echo
        self.rx = b""
        self.locked_writes = 0

    def reset_input_buffer(self):
        self.rx = b""

    def read(self, n):
        out, self.rx = self.rx[:n], self.rx[n:]
        return out

    def write(self, data):
        assert data[:2] == b"\xff\xff" and feetech.checksum(data[2:-1]) == data[-1], data.hex()
        sid, length, instr, params = data[2], data[3], data[4], data[5:-1]
        assert length == len(params) + 2
        if self.echo:
            self.rx += data
        for i, m in list(self.mem.items()):
            if sid not in (i, feetech.BROADCAST_ID):
                continue
            reply = b""
            if instr == feetech.READ:
                reply = bytes(m[params[0]:params[0] + params[1]])
            elif instr == feetech.WRITE:
                reg = params[0]
                if reg < feetech.REG_TORQUE_ENABLE and m[feetech.REG_LOCK]:
                    self.locked_writes += 1      # a real servo would not keep this
                m[reg:reg + len(params) - 1] = params[1:]
                if m[feetech.REG_ID] != i:       # renumbered: takes effect at once
                    self.mem[m[feetech.REG_ID]] = self.mem.pop(i)
            if sid != feetech.BROADCAST_ID:
                self.rx += feetech.packet(i, 0, reply)


check(feetech.packet(1, feetech.PING).hex() == "ffff010201fb", "ping packet for ID 1 should be FF FF 01 02 01 FB")
check(feetech.to_signed(feetech.from_signed(-5000)) == -5000, "sign-magnitude round trip")
check(feetech.from_signed(-1) == 0x8001, "-1 should encode as 0x8001")

for echo in (False, True):
    port = FakeServoPort([1], echo=echo)
    bus = feetech.Bus(port)
    tag = f"(echo={echo})"
    check(bus.scan() == [1], f"scan finds servo 1 {tag}")
    check(not bus.ping(7), f"no reply from a servo that is not there {tag}")

    bus.set_id(1, 4)
    check(bus.scan() == [4], f"set_id 1 -> 4 {tag}")
    check(port.mem[4][feetech.REG_LOCK] == 1, f"EPROM re-locked under the new ID {tag}")

    bus.ensure_multi_turn(4)
    check(bus.read_word(4, feetech.REG_MAX_ANGLE_LIMIT) == 0, f"multi-turn: max limit 0 {tag}")
    writes_before = port.locked_writes
    bus.ensure_multi_turn(4)
    check(port.locked_writes == 0 and writes_before == 0, f"no EPROM write while locked {tag}")

    bus.move_to(4, -9000, 2400, 30)
    m = port.mem[4]
    check(m[feetech.REG_ACC] == 30, f"move_to writes acc {tag}")
    check(feetech.to_signed(int.from_bytes(m[42:44], "little")) == -9000, f"move_to writes goal position {tag}")

    # snapshot(): one read of registers 56-70 decoded like the single reads
    m[56:58] = feetech.from_signed(-1234).to_bytes(2, "little")
    m[58:60] = feetech.from_signed(-300).to_bytes(2, "little")
    m[60:62] = (0x400 | 250).to_bytes(2, "little")          # load: bit 10 is the sign
    m[62], m[63], m[65], m[66] = 73, 31, 0x20, 1
    m[69:71] = (40).to_bytes(2, "little")
    snap = bus.snapshot(4)
    check(snap == {"position": -1234, "speed": -300, "load_per_mille": -250, "volts": 7.3, "temp_c": 31,
                   "status": 0x20, "moving": True, "current_ma": 260}, f"snapshot decodes registers 56-70 {tag}: {snap}")
    check(snap["position"] == bus.position(4), f"snapshot position matches position() {tag}")
    check(int.from_bytes(m[46:48], "little") == 2400, f"move_to writes goal speed {tag}")

    m[56:58] = feetech.from_signed(-123).to_bytes(2, "little")
    check(bus.position(4) == -123, f"position reads back signed {tag}")
print("servo driver: fake-servo checks done")


# ---- 3. dial and step logic --------------------------------------------------

d = orrery.Dial(date(2027, 1, 31))
d.step = 2
d.turn(1)
check(d.day == date(2027, 2, 28), f"31 Jan + 1 month = 28 Feb, got {d.day}")
d.turn(1)
check(d.day == date(2027, 3, 31), f"... + 1 month = 31 Mar, got {d.day}")
d.step = 3
d.turn(-1)
check(d.day == date(2026, 3, 31), f"- 1 year, got {d.day}")
d.turn(-5000)
check(d.day == orrery.DAY_MIN, "dial stops at 1800")
d.turn(5000)
check(d.day == orrery.DAY_MAX, "dial stops at 2200")

S = orrery.STEPS_PER_TURN
check(orrery.steps_for_angle(90, 0, 0) == S // 4, "90 deg from rest = 1024 steps")
check(orrery.steps_for_angle(350, 0, 0) == -S * 10 // 360 + 0 or
      abs(orrery.steps_for_angle(350, 0, 0) + 114) <= 1, "350 deg from 0 goes backwards 10 deg")
check(orrery.steps_for_angle(10, 0, 3 * S - 50) == 3 * S + 114, "keeps counting up past a lap")
check(abs(orrery.steps_for_angle(350, 0, 0, 2) - (S * 350 // 360)) <= 1, "forward only: 350 deg from 0 goes forward 350 deg")
check(orrery.steps_for_angle(359, 0, 0, 2) == 0, "forward only: 1 deg behind (within 2) stays put, no lap, no nudge back")
check(orrery.steps_for_angle(355, 0, 0, 2) > 0, "forward only: 5 deg behind goes on forward, never back")
check(orrery.steps_for_angle(340, 0, 0, 30) == 0, "start-up: 20 deg behind (within 30) stays put")
check(abs(orrery.steps_for_angle(340, 0, 0, 2) - S * 340 // 360) <= 1, "forward only: 20 deg behind goes on 340 deg")
check(orrery.steps_for_angle(10, 0, 3 * S - 50, 2) == 3 * S + 114, "forward only: keeps counting up past a lap")
check(orrery.steps_for_angle(90, 0, S // 4, 2) == S // 4, "forward only: already there stays put")
pos = 0
for lap in range(40):                       # Mercury going round and round
    for deg in (90, 180, 270, 0):
        new = orrery.steps_for_angle(deg, 0, pos)
        check(abs(new) <= orrery.STEP_LIMIT, "stays inside the multi-turn counter")
        check((new - round(deg * S / 360)) % S == 0, "always points the right way")
        pos = new
check(feetech.from_signed(orrery.STEP_LIMIT) > 0, "step limit fits the 15-bit position word")

# ---- Line-up calibration (8 Nov 2026) ----
saved_home = list(orrery.HOME_STEPS)
for h in (0, 1234, 4095):
    orrery.HOME_STEPS[2] = h
    orrery.zero_from_home()
    at = orrery.steps_for_angle(orrery.HOME_LON, orrery.ARM_ZERO_DEG[2], 5000) % S
    check(min(abs(at - h), S - abs(at - h)) <= 1, f"home {h}: LINE UP sends Earth's servo back to {h} ({at})")
    check(abs(orrery.from_line(2, h + 3 * S)) < 1e-9, f"home {h}: on the line reads 0 deg, whatever the turn count")
    check(abs(orrery.from_line(2, h + S // 36) - orrery.ARM_DIR * 10) < 0.1, f"home {h}: 114 steps on = 10 deg off the line")
orrery.HOME_STEPS[2] = None
orrery.zero_from_home()
check(orrery.home_step(2) == 1024 and abs(orrery.from_line(2, 1024)) < 1e-9, "no saved home: travel mode is servo step 1024 (90 deg)")
import json as _json, tempfile as _tf
from pathlib import Path as _P
_real, orrery.HOME_FILE = orrery.HOME_FILE, _P(_tf.mkdtemp()) / "home.json"
orrery.HOME_FILE.write_text(_json.dumps({"home_steps": [100] + [None] * 7, "lined_up": False, "home_lon": 270.0}))
orrery.load_home()
check(orrery.HOME_STEPS[0] == (100 - 2048) % S, f"a home saved when the line pointed at the screen is turned half a turn ({orrery.HOME_STEPS[0]})")
orrery.HOME_FILE = _real
orrery.HOME_STEPS[:] = saved_home
orrery.zero_from_home()

print(f"{failures} FAILURES" if failures else "all checks passed")
raise SystemExit(failures != 0)
