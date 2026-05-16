"""Higher-level interface for Brutus28 boards.

Brutus28 exposes an interactive text command shell over USB CDC rather than
the binary protocol used by the dupico firmware. This adapter keeps the same
BoardCommandsInterface shape so host tools can reuse the existing dumping
logic.
"""

from __future__ import annotations

import re
import time
from typing import Callable, Dict, final

import serial

from dupicolib.hardware_board_commands import HardwareBoardCommands

_PROMPT = b"CMD>"
_READ_CHUNK_SIZE = 1
_MAX_PIN_MASK = (1 << 28) - 1


@final
class Brutus28BoardCommands(HardwareBoardCommands):
    """Board command adapter for Chris Hooper's Brutus28."""

    MODEL = 28

    _PIN_NUMBER_TO_INDEX_MAP: Dict[int, int] = {
        1: 0, 2: 1, 3: 2, 4: 3,
        5: 4, 6: 5, 7: 6, 8: 7,
        9: 8, 10: 9, 11: 10, 12: 11,
        13: 12, 14: 13, 15: 14, 16: 15,
        17: 16, 18: 17, 19: 18, 20: 19,
        21: 20, 22: 21, 23: 22, 24: 23,
        25: 24, 26: 25, 27: 26, 28: 27,
        0: -1,
    }

    _INPUT_RE = re.compile(r"Input=([01]{1,28})")
    _LAST_OUTPUT_MASK_BY_SERIAL_ID: Dict[int, int] = {}

    @staticmethod
    def _read_until_prompt(ser: serial.Serial, timeout: float | None = None) -> str:
        deadline = None if timeout is None else time.monotonic() + timeout
        data = bytearray()

        while True:
            if deadline is not None and time.monotonic() > deadline:
                raise TimeoutError("Timed out waiting for Brutus28 prompt")

            chunk = ser.read(_READ_CHUNK_SIZE)
            if not chunk:
                continue

            data.extend(chunk)
            if data.rstrip().endswith(_PROMPT):
                return data.decode("ASCII", errors="replace")

    @classmethod
    def _send_text_command(cls, ser: serial.Serial, command: str, timeout: float | None = 5.0) -> str:
        ser.write(f"{command}\r".encode("ASCII"))
        return cls._read_until_prompt(ser, timeout)

    @classmethod
    def initialize_connection(cls, ser: serial.Serial, retries: int = 3) -> bool:
        """Synchronize with the Brutus28 command prompt."""

        for _ in range(retries):
            ser.reset_input_buffer()
            ser.write(b"\r")
            try:
                cls._read_until_prompt(ser, 2.0)
                return True
            except TimeoutError:
                continue

        return False

    @staticmethod
    def get_model(ser: serial.Serial | None = None) -> int | None:
        return Brutus28BoardCommands.MODEL

    @staticmethod
    def get_version(ser: serial.Serial | None = None) -> str | None:
        if ser is None:
            return None

        output = Brutus28BoardCommands._send_text_command(ser, "version")
        for line in output.splitlines():
            if "Version" in line:
                return line.strip()

        return None

    @staticmethod
    def test_board(ser: serial.Serial | None = None) -> bool | None:
        if ser is None:
            return None

        output = Brutus28BoardCommands._send_text_command(ser, "pld check", timeout=30.0)
        upper_output = output.upper()
        if "FAIL" in upper_output:
            return False
        return "CMD>" in output

    @staticmethod
    def set_power(state: bool, ser: serial.Serial | None = None) -> bool | None:
        if ser is None:
            return None

        command = "pld enable" if state else "pld disable"
        output = Brutus28BoardCommands._send_text_command(ser, command)
        if "CMD>" not in output:
            return None

        if state:
            pins = Brutus28BoardCommands._LAST_OUTPUT_MASK_BY_SERIAL_ID.get(id(ser), 0)
            if pins and Brutus28BoardCommands.write_pins(pins, ser) is None:
                return None

        return True

    @staticmethod
    def write_pins(pins: int, ser: serial.Serial | None = None) -> int | None:
        if ser is None:
            return None

        pins &= _MAX_PIN_MASK
        output = Brutus28BoardCommands._send_text_command(ser, f"pld output 0x{pins:x}")
        if "CMD>" not in output:
            return None
        Brutus28BoardCommands._LAST_OUTPUT_MASK_BY_SERIAL_ID[id(ser)] = pins
        return pins

    @staticmethod
    def read_pins(ser: serial.Serial | None = None) -> int | None:
        if ser is None:
            return None

        output = Brutus28BoardCommands._send_text_command(ser, "pld input")
        match = Brutus28BoardCommands._INPUT_RE.search(output)
        if not match:
            return None

        return int(match.group(1), 2)

    @staticmethod
    def detect_osc_pins(reads: int, ser: serial.Serial | None = None) -> int | None:
        if ser is None or reads <= 0:
            return None

        first_read = Brutus28BoardCommands.read_pins(ser)
        if first_read is None:
            return None

        changed = 0
        previous = first_read
        for _ in range(reads - 1):
            current = Brutus28BoardCommands.read_pins(ser)
            if current is None:
                return None

            changed |= previous ^ current
            previous = current

        return changed

    @classmethod
    def cxfer_read(cls, address_pins: list[int], data_pins: list[int], hi_pins: list[int], update_callback: Callable[[int], None] | None, ser: serial.Serial | None = None) -> bytes | None:
        if ser is None:
            return None

        data = bytearray()
        address_count = 1 << len(address_pins)
        data_width = -(len(data_pins) // -8)
        hi_pin_mask = cls.map_value_to_pins(hi_pins, _MAX_PIN_MASK)

        for address in range(address_count):
            address_mask = cls.map_value_to_pins(address_pins, address)
            if cls.write_pins(hi_pin_mask | address_mask, ser) is None:
                return None

            read_mask = cls.read_pins(ser)
            if read_mask is None:
                return None

            value = cls.map_pins_to_value(data_pins, read_mask)
            data.extend(value.to_bytes(data_width, "big"))

            if update_callback is not None:
                update_callback(len(data))

        return bytes(data)

    @classmethod
    def map_value_to_pins(cls, pins: list[int], value: int) -> int:
        return cls._map_value_to_pins(cls._PIN_NUMBER_TO_INDEX_MAP, pins, value)

    @classmethod
    def map_pins_to_value(cls, pins: list[int], value: int) -> int:
        return cls._map_pins_to_value(cls._PIN_NUMBER_TO_INDEX_MAP, pins, value)
