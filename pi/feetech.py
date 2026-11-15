"""Minimal driver for Feetech STS-series serial-bus servos (STS3215).

Talks to the bus through the driver board's USB socket, which shows up as an
ordinary serial port (/dev/ttyUSB0 or /dev/ttyACM0 on the Pi,
/dev/cu.usbmodem* or /dev/cu.wchusbserial* on a Mac). Only needs pyserial.

Packet, both directions:  FF FF  id  len  instr-or-error  params...  checksum
  len = params + 2,  checksum = ~(id + len + instr + params) & 0xFF
Two-byte values are little-endian. Position and speed use bit 15 as a sign bit
(sign-magnitude, not two's complement).

Register numbers are from Feetech's SMS_STS.h.
"""

import time

BROADCAST_ID = 254

PING, READ, WRITE = 1, 2, 3

# EPROM (kept through power-off; needs unlock before writing)
REG_ID = 5
REG_MIN_ANGLE_LIMIT = 9
REG_MAX_ANGLE_LIMIT = 11
REG_MODE = 33            # 0 = position, 1 = constant speed (wheel)
# RAM
REG_TORQUE_ENABLE = 40
REG_ACC = 41
REG_GOAL_POSITION = 42
REG_GOAL_SPEED = 46
REG_TORQUE_LIMIT = 48    # 0..1000 = 0..100 %
REG_LOCK = 55            # 0 = EPROM writable, 1 = locked
REG_PRESENT_POSITION = 56
REG_PRESENT_SPEED = 58
REG_PRESENT_LOAD = 60
REG_PRESENT_VOLTAGE = 62  # 0.1 V units
REG_PRESENT_TEMPERATURE = 63
REG_STATUS = 65          # protection trips: see STATUS_BITS
REG_MOVING = 66
REG_PRESENT_CURRENT = 69  # ~6.5 mA a unit (30 Sep 2026: 5-120 mA spinning free)
CURRENT_MA = 6.5

# Status byte (65): the servo's own protections. When one trips the servo switches
# its motor off (limp) until torque is enabled again.
STATUS_BITS = {0x01: "low voltage", 0x04: "too hot", 0x08: "too much current", 0x20: "overload"}

STEPS_PER_TURN = 4096


class ServoError(Exception):
    pass


def checksum(body):
    return ~sum(body) & 0xFF


def packet(servo_id, instr, params=b""):
    body = bytes([servo_id, len(params) + 2, instr]) + bytes(params)
    return b"\xff\xff" + body + bytes([checksum(body)])


def to_signed(word):
    return -(word & 0x7FFF) if word & 0x8000 else word


def from_signed(value):
    if not -0x7FFF <= value <= 0x7FFF:
        raise ValueError(f"{value} does not fit a sign-magnitude word")
    return (-value | 0x8000) if value < 0 else value


class Bus:
    def __init__(self, port, baud=1_000_000, timeout=0.05):
        """`port` is a device path, or any object with read/write/reset_input_buffer
        (the tests pass a fake)."""
        if isinstance(port, str):
            import serial
            port = serial.Serial(port, baud, timeout=timeout)
        self.port = port
        self.echo = self._adapter_echoes()

    def _adapter_echoes(self):
        """Some adapters loop what was sent back onto RX. Ask a servo that is not
        there (ID 253) for its position: if the exact packet comes back, that is
        an echo, and every later reply has to skip it. A ping cannot be used for
        this, because a ping's echo is byte-for-byte a valid ping reply."""
        out = packet(253, READ, [REG_PRESENT_POSITION, 2])
        self.port.reset_input_buffer()
        self.port.write(out)
        return self.port.read(len(out)) == out

    def close(self):
        self.port.close()

    # ---- raw protocol ----

    def _transact(self, servo_id, instr, params=b"", reply_params=0):
        out = packet(servo_id, instr, params)
        self.port.reset_input_buffer()
        self.port.write(out)
        if self.echo:
            self.port.read(len(out))
        if servo_id == BROADCAST_ID:
            return b""
        want = 6 + reply_params
        data = self.port.read(want)
        if len(data) < want:
            raise ServoError(f"servo {servo_id}: no reply")
        if data[:2] != b"\xff\xff" or data[2] != servo_id or data[3] != reply_params + 2:
            raise ServoError(f"servo {servo_id}: garbled reply {data.hex()}")
        if checksum(data[2:-1]) != data[-1]:
            raise ServoError(f"servo {servo_id}: bad checksum {data.hex()}")
        # data[4] is the servo's error/status byte (overload, voltage, heat). It
        # is a warning, not a comms failure, so it is not raised here.
        return data[5:-1]

    def ping(self, servo_id):
        try:
            self._transact(servo_id, PING)
            return True
        except ServoError:
            return False

    def read_byte(self, servo_id, reg):
        return self._transact(servo_id, READ, [reg, 1], 1)[0]

    def read_word(self, servo_id, reg):
        lo, hi = self._transact(servo_id, READ, [reg, 2], 2)
        return lo | hi << 8

    def write_byte(self, servo_id, reg, value):
        self._transact(servo_id, WRITE, [reg, value & 0xFF])

    def write_word(self, servo_id, reg, value):
        self._transact(servo_id, WRITE, [reg, value & 0xFF, value >> 8 & 0xFF])

    # ---- servo operations ----

    def scan(self, ids=range(0, 254)):
        return [i for i in ids if self.ping(i)]

    def write_eprom(self, servo_id, writes):
        """writes = [(reg, value, 'byte'|'word'), ...] done inside one unlock/lock."""
        self.write_byte(servo_id, REG_LOCK, 0)
        try:
            for reg, value, size in writes:
                (self.write_byte if size == "byte" else self.write_word)(servo_id, reg, value)
        finally:
            # An ID change takes effect at once, so re-lock under the new ID.
            new_id = next((v for r, v, _ in writes if r == REG_ID), servo_id)
            time.sleep(0.01)
            self.write_byte(new_id, REG_LOCK, 1)

    def set_id(self, old_id, new_id):
        self.write_eprom(old_id, [(REG_ID, new_id, "byte")])

    def ensure_multi_turn(self, servo_id):
        """Both angle limits 0 = multi-turn position mode, so a planet can keep
        turning past one lap. EPROM wears, so only write when it is not already right."""
        if (self.read_byte(servo_id, REG_MODE) == 0 and
                self.read_word(servo_id, REG_MIN_ANGLE_LIMIT) == 0 and
                self.read_word(servo_id, REG_MAX_ANGLE_LIMIT) == 0):
            return
        self.write_eprom(servo_id, [(REG_MODE, 0, "byte"),
                                    (REG_MIN_ANGLE_LIMIT, 0, "word"),
                                    (REG_MAX_ANGLE_LIMIT, 0, "word")])

    def set_mode(self, servo_id, mode):
        if self.read_byte(servo_id, REG_MODE) != mode:
            self.write_eprom(servo_id, [(REG_MODE, mode, "byte")])

    def set_torque_limit(self, servo_id, per_mille):
        self.write_word(servo_id, REG_TORQUE_LIMIT, per_mille)

    def enable_torque(self, servo_id, on=True):
        self.write_byte(servo_id, REG_TORQUE_ENABLE, 1 if on else 0)

    def move_to(self, servo_id, steps, speed, acc):
        """One write covering acc (41), goal position (42-43), goal time (44-45), goal speed (46-47)."""
        pos = from_signed(steps)
        self._transact(servo_id, WRITE, [REG_ACC, acc,
                                         pos & 0xFF, pos >> 8, 0, 0,
                                         speed & 0xFF, speed >> 8])

    def set_speed(self, servo_id, steps_per_s, acc):
        """Constant-speed mode only (set_mode(id, 1))."""
        self.write_byte(servo_id, REG_ACC, acc)
        self.write_word(servo_id, REG_GOAL_SPEED, from_signed(steps_per_s))

    def position(self, servo_id):
        return to_signed(self.read_word(servo_id, REG_PRESENT_POSITION))

    def is_moving(self, servo_id):
        return self.read_byte(servo_id, REG_MOVING) != 0

    def snapshot(self, servo_id):
        """Everything that changes, in ONE read of registers 56-70: 0.61 ms a servo on
        the Pi, against 0.46 ms for the position alone (measured 2 Oct 2026), so the
        motion loop reads it for every arm, every tick."""
        r = self._transact(servo_id, READ, [REG_PRESENT_POSITION, 15], 15)
        word = lambda reg: r[reg - REG_PRESENT_POSITION] | r[reg - REG_PRESENT_POSITION + 1] << 8
        return {
            "position": to_signed(word(REG_PRESENT_POSITION)),
            "speed": to_signed(word(REG_PRESENT_SPEED)),
            "load_per_mille": to_signed_load(word(REG_PRESENT_LOAD)),
            "volts": r[REG_PRESENT_VOLTAGE - REG_PRESENT_POSITION] / 10,
            "temp_c": r[REG_PRESENT_TEMPERATURE - REG_PRESENT_POSITION],
            "status": r[REG_STATUS - REG_PRESENT_POSITION],
            "moving": r[REG_MOVING - REG_PRESENT_POSITION] != 0,
            "current_ma": round(to_signed(word(REG_PRESENT_CURRENT)) * CURRENT_MA),
        }

    def status(self, servo_id):
        """snapshot() plus the mode and angle limits (for servo_tool.py and friends)."""
        return {
            **self.snapshot(servo_id),
            "mode": self.read_byte(servo_id, REG_MODE),
            "min_limit": self.read_word(servo_id, REG_MIN_ANGLE_LIMIT),
            "max_limit": self.read_word(servo_id, REG_MAX_ANGLE_LIMIT),
        }


def to_signed_load(word):
    # Load uses bit 10 as its sign bit.
    return -(word & 0x3FF) if word & 0x400 else word & 0x3FF
