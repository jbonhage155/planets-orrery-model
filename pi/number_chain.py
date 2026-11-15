#!/usr/bin/env python3
"""Number servos one at a time as they are added to the end of a chain.

Every STS3215 leaves the factory as ID 1. Run this, then add servos to the bus
one by one (power off, plug the next one on, power on). Each time a factory-fresh
servo (ID 1) appears next to the ones already numbered, it gets the next number
and wiggles so you can see which one it was.

    python3 number_chain.py            # numbers 2..6 (Mercury keeps ID 1, goes on last)
    python3 number_chain.py --last 9 --have 2 3 4 5 6   # later: Uranus, Neptune, Pluto
    python3 number_chain.py --roll-call     # wiggle every servo on the bus in ID order

On 25 Sep 2026 servos 2-6 were numbered one at a time, each alone on the board,
which works as well as building the chain up and is harder to get wrong.

After the last number, plug Mercury (ID 1) in and it confirms the whole chain.
"""

import argparse
import time

from feetech import Bus, ServoError
from orrery import find_port

NAMES = {1: "Mercury", 2: "Venus", 3: "Earth", 4: "Mars", 5: "Jupiter",
         6: "Saturn", 7: "Uranus", 8: "Neptune", 9: "Pluto", 10: "spare"}


def one_servo_at(bus, sid):
    """Two servos on the same ID answer on top of each other: the replies mostly
    collide and fail their checksum. Several clean reads = very likely just one."""
    try:
        reads = {bus.position(sid) for _ in range(4)}
    except ServoError:
        return False
    return max(reads) - min(reads) < 20


def wiggle(bus, sid):
    p = bus.position(sid)
    t = p + 300 if p < 3700 else p - 300          # ~26 degrees
    bus.set_torque_limit(sid, 500)
    bus.enable_torque(sid)
    for goal in (t, p, t, p):
        bus.move_to(sid, goal, 1500, 50)
        time.sleep(0.5)
    bus.enable_torque(sid, False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--first", type=int, default=2)
    ap.add_argument("--last", type=int, default=6)
    ap.add_argument("--have", type=int, nargs="*", default=[],
                    help="IDs already handed out earlier, e.g. --have 2 3")
    ap.add_argument("--roll-call", action="store_true", help="wiggle each servo on the bus in ID order")
    args = ap.parse_args()
    if args.roll_call:
        bus = Bus(find_port())
        found = bus.scan(range(1, 12))
        print("on the bus:", found, flush=True)
        for sid in found:
            st = bus.status(sid)
            print(f"{sid} {NAMES.get(sid, ''):8} {'one servo' if one_servo_at(bus, sid) else 'DUPLICATE ID'}  "
                  f"{st['volts']:.1f} V  {st['temp_c']} C  - wiggling", flush=True)
            wiggle(bus, sid)
            time.sleep(1)
        return
    wanted = list(range(args.first, args.last + 1))
    have = set(args.have)   # numbers handed out so far (never reused)
    bus = Bus(find_port())
    first = [n for n in wanted if n not in have][0]
    print(f"waiting: add the servo for ID {first} ({NAMES.get(first, '')}) on its own", flush=True)
    seen = None
    while True:
        found = bus.scan(range(1, args.last + 3))
        if found != seen:
            print(f"on the bus now: {found or 'nothing (power on?)'}", flush=True)
            seen = found
        # Numbers handed out are remembered (and --have), not inferred from the bus:
        # on 25 Sep Venus dropped off the chain when Earth was added, and inferring
        # "2 is missing, so give it out" made Earth a second ID 2.
        todo = [n for n in wanted if n not in have and n not in found]
        if not todo:
            full = [1] + sorted(have | set(found) - {1})
            if found == full and len(found) >= len(wanted) + 1:
                print(f"DONE: whole chain answers {found}", flush=True)
                return
        elif 1 in found:
            new = todo[0]
            if new in found:
                print(f"ID {new} is already on the bus; not reusing it", flush=True)
                time.sleep(3)
                continue
            if not one_servo_at(bus, 1):
                print("ID 1 answers garbled: more than one un-numbered servo on the bus. "
                      "Power off and leave only one new servo on.", flush=True)
                time.sleep(3)
                continue
            bus.set_id(1, new)
            time.sleep(0.2)
            if bus.ping(new) and not bus.ping(1):
                have.add(new)
                print(f"numbered {new} ({NAMES.get(new, '')}) - wiggling it now", flush=True)
                wiggle(bus, new)
                nxt = [n for n in todo if n != new]
                print(f"next: power off, add {'ID %d (%s)' % (nxt[0], NAMES.get(nxt[0], '')) if nxt else 'Mercury (ID 1)'} "
                      "(on its own, or on the end of the chain), power on", flush=True)
            else:
                print(f"set-id to {new} did not verify; will retry", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
