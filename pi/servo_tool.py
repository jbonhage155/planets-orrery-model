#!/usr/bin/env python3
"""Bench tool for the STS3215 servos. Works from a Mac or the Pi: plug the
driver board into USB (jumper on the USB side), power the board at 7.5 V.

    python3 servo_tool.py scan                 # who is on the bus?
    python3 servo_tool.py info 1               # position, volts, temperature, mode
    python3 servo_tool.py set-id 3             # renumber the ONE connected servo to 3
    python3 servo_tool.py goto 1 90            # point servo 1 at 90 degrees
    python3 servo_tool.py spin 1 --rpm 20      # the phase-0 smoothness test; Ctrl-C stops

set-id: exactly one servo connected. They all answer to ID 1 out of the box, so
two at once would both take the new number and neither could be addressed after.
"""

import argparse
import sys
import time

from feetech import Bus, STEPS_PER_TURN
from orrery import SERVO_ACC, SERVO_SPEED, SERVO_TORQUE_LIMIT, find_port


def cmd_scan(bus, args):
    found = bus.scan()
    print("servos answering:", found or "none (check 7.5 V power, the USB jumper, the cable)")


def cmd_info(bus, args):
    for k, v in bus.status(args.id).items():
        print(f"{k:15} {v}")


def cmd_set_id(bus, args):
    if not 1 <= args.new_id <= 253:
        sys.exit("ID must be 1..253")
    found = bus.scan()
    if len(found) != 1:
        sys.exit(f"Need exactly one servo on the bus, found {found}. Nothing changed.")
    if found[0] != args.new_id:
        bus.set_id(found[0], args.new_id)
    ok = bus.ping(args.new_id)
    print(f"ID {found[0]} -> {args.new_id} {'OK' if ok else 'FAILED: no reply on the new ID'}")


def cmd_goto(bus, args):
    bus.ensure_multi_turn(args.id)
    bus.set_torque_limit(args.id, args.torque)
    bus.enable_torque(args.id)
    bus.move_to(args.id, round(args.deg % 360 * STEPS_PER_TURN / 360), SERVO_SPEED, SERVO_ACC)
    time.sleep(0.1)
    while bus.is_moving(args.id):
        time.sleep(0.05)
    print("now at", round(bus.position(args.id) * 360 / STEPS_PER_TURN, 1), "deg")


def cmd_spin(bus, args):
    # 20 rpm = Mercury's speed in Run mode, the fastest anything in the model turns.
    speed = round(args.rpm / 60 * STEPS_PER_TURN)
    bus.set_mode(args.id, 1)
    bus.set_torque_limit(args.id, args.torque)
    bus.enable_torque(args.id)
    print(f"servo {args.id} at {args.rpm} rpm ({speed} steps/s), torque cap {args.torque / 10:.0f} %. Ctrl-C to stop.")
    try:
        bus.set_speed(args.id, speed, SERVO_ACC)
        while True:
            s = bus.status(args.id)
            print(f"\r  speed {s['speed']:5}  load {s['load_per_mille'] / 10:5.1f} %  "
                  f"{s['volts']:.1f} V  {s['temp_c']} C ", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()
    finally:
        bus.set_speed(args.id, 0, SERVO_ACC)
        time.sleep(0.5)
        bus.enable_torque(args.id, False)
        bus.set_mode(args.id, 0)   # back to position mode, which is what orrery.py expects


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="serial port (default: auto-detect)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan").set_defaults(fn=cmd_scan)
    p = sub.add_parser("info"); p.add_argument("id", type=int); p.set_defaults(fn=cmd_info)
    p = sub.add_parser("set-id"); p.add_argument("new_id", type=int); p.set_defaults(fn=cmd_set_id)
    for name, fn in (("goto", cmd_goto), ("spin", cmd_spin)):
        p = sub.add_parser(name)
        p.add_argument("id", type=int)
        if name == "goto":
            p.add_argument("deg", type=float)
        else:
            p.add_argument("--rpm", type=float, default=20)
        p.add_argument("--torque", type=int, default=SERVO_TORQUE_LIMIT, help="0..1000, default %(default)s")
        p.set_defaults(fn=fn)
    args = ap.parse_args()

    bus = Bus(args.port or find_port())
    try:
        args.fn(bus, args)
    finally:
        bus.close()


if __name__ == "__main__":
    main()
