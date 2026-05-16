"""Tests for Brutus28 board commands."""

# pylint: disable=wrong-import-position,wrong-import-order

import sys
sys.path.insert(0, '.') # Make VSCode happy...

from collections.abc import Callable

from dupicolib.board_interfaces.brutus28_board_commands import Brutus28BoardCommands


class FakeBrutusSerial:
    """Small command-shell fake for the Brutus28 text protocol."""

    def __init__(self, input_provider: Callable[[int], int] | None = None):
        self.input_provider = input_provider
        self.last_output = 0
        self.writes: list[str] = []
        self._rx = bytearray()

    def reset_input_buffer(self):
        self._rx.clear()

    def write(self, data: bytes):
        command = data.decode("ASCII").strip()
        self.writes.append(command)

        if not command:
            self._queue("CMD> ")
        elif command == "version":
            self._queue("Version 0.3 built TEST\r\nCMD> ")
        elif command == "pld check":
            self._queue("OK\r\nCMD> ")
        elif command in ("pld enable", "pld disable"):
            self._queue("CMD> ")
        elif command.startswith("pld output "):
            self.last_output = int(command.split()[-1], 0)
            self._queue("CMD> ")
        elif command == "pld input":
            value = self.input_provider(self.last_output) if self.input_provider else self.last_output
            self._queue(f"Input={value:028b}\r\nCMD> ")
        else:
            self._queue(f"Unknown command {command}\r\nCMD> ")

    def read(self, size: int = 1) -> bytes:
        if not self._rx:
            return b""

        data = self._rx[:size]
        del self._rx[:size]
        return bytes(data)

    def _queue(self, text: str):
        self._rx.extend(text.encode("ASCII"))


def test_brutus28_initialize_and_version():
    ser = FakeBrutusSerial()

    assert Brutus28BoardCommands.initialize_connection(ser)
    assert Brutus28BoardCommands.get_model() == 28
    assert Brutus28BoardCommands.get_version(ser) == "Version 0.3 built TEST"


def test_brutus28_pin_mapping():
    assert Brutus28BoardCommands.map_value_to_pins([1, 2, 10, 19, 28], 0b11111) == 0x8040203
    assert Brutus28BoardCommands.map_value_to_pins([1, 2, 10, 19, 28], 0b10101) == 0x8000201
    assert Brutus28BoardCommands.map_pins_to_value([1, 2, 10, 19, 28], 0x8040203) == 0b11111
    assert Brutus28BoardCommands.map_pins_to_value([1, 2, 10, 19, 28], 0x8000201) == 0b10101
    assert Brutus28BoardCommands.map_value_to_pins([21], 1) == 0x100000
    assert Brutus28BoardCommands.map_pins_to_value([21], 0x100000) == 1


def test_brutus28_read_write_pins():
    ser = FakeBrutusSerial()

    assert Brutus28BoardCommands.set_power(True, ser)
    assert Brutus28BoardCommands.write_pins(0x1234567, ser) == 0x1234567
    assert Brutus28BoardCommands.read_pins(ser) == 0x1234567
    assert Brutus28BoardCommands.set_power(False, ser)


def test_brutus28_power_on_reapplies_last_output_mask():
    ser = FakeBrutusSerial()

    assert Brutus28BoardCommands.write_pins(0x123, ser) == 0x123
    assert Brutus28BoardCommands.set_power(True, ser)

    assert ser.writes[-2:] == ["pld enable", "pld output 0x123"]


def test_brutus28_cxfer_read():
    def input_provider(last_output: int) -> int:
        address = Brutus28BoardCommands.map_pins_to_value([1, 2], last_output)
        data = address ^ 0x2
        return last_output | Brutus28BoardCommands.map_value_to_pins([3, 4], data)

    ser = FakeBrutusSerial(input_provider)
    updates: list[int] = []

    data = Brutus28BoardCommands.cxfer_read([1, 2], [3, 4], [5], updates.append, ser)

    assert data == bytes([2, 3, 0, 1])
    assert updates == [1, 2, 3, 4]
    assert "pld output 0x10" in ser.writes
    assert "pld output 0x13" in ser.writes
