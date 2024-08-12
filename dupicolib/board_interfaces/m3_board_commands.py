"""This module contains higher-level code for board interfacing"""

from typing import Dict, final
import struct
from enum import Enum

import serial

from dupicolib.board_utilities import BoardUtilities
from dupicolib.board_commands import BoardCommands

class CommandCode(Enum):
    WRITE = 0
    READ = 1
    RESET = 2
    POWER = 3
    TEST = 5

@final
class M3BoardCommands(BoardCommands):
    # The following map is used to associate a pin number (e.g. pin 1 or 10) on the socket
    # with the corresponding bit index used to access said pin by the dupico.
    # Negative numbers will be ignored in the mapping
    PIN_NUMBER_TO_INDEX_MAP: Dict[int, int] = {
        1: 0, 2: 1, 3: 2,
        4: 3, 5: 4, 6: 5,
        7: 6, 8: 7, 9: 8,
        10: 9, 11: 10, 12: 11,
        13: 12, 14: 13, 15: 14,
        16: 15, 17: 16, 18: 17,
        19: 18, 20: 19, 22: 20,
        23: 21, 24: 22, 25: 23,
        26: 24, 27: 25, 28: 26,
        29: 27, 30: 28, 31: 29,
        32: 30, 33: 31, 34: 32,
        35: 33, 36: 34, 37: 35,
        38: 36, 39: 37, 40: 38,
        41: 39, 21: -1, 42: -1
    } 

    @staticmethod
    def test_board(ser: serial.Serial) -> bool | None:
        """Perform a minimal self-test of the board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            bool | None: True if test passed correctly, False otherwise
        """        
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.TEST.value]), 1)

        if res is not None:
            return res[0] == 1
        else:
            return None
        
    @staticmethod
    def set_power(ser: serial.Serial, state: bool) -> bool | None:
        """Enable or disable the power on the socket VCC

        Args:
            ser (serial.Serial): serial port on which to send the command
            state (bool): True if we wish power applied, False otherwise

        Returns:
            bool | None: True if power was applied, False otherwise, None in case we did not read the response correctly
        """
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.POWER.value, 1 if state else 0]), 1)

        if res is not None:
            return res[0] == 1
        else:
            return None
        
    @staticmethod
    def write_pins(ser: serial.Serial, pins: int) -> int | None:
        """Toggle the specified pins and read their status back

        Args:
            ser (serial.Serial): serial port on which to send the command
            pins (int): value that the pins will be set to. A bit set to '1' means that the pin will be pulled high

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """                
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.WRITE.value, *struct.pack('<Q', pins)]), 8)

        if res is not None:
            return struct.unpack('<Q', res)[0]
        else:
            return None
        
    @staticmethod
    def read_pins(ser: serial.Serial) -> int | None:
        """Read the value of the pins

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """        
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.READ.value]), 8)

        if res is not None:
            return struct.unpack('<Q', res)[0]
        else:
            return None
        
    @classmethod
    def map_value_to_pins(cls, pins: list[int], value: int) -> int:
        return cls._map_value_to_pins(cls.PIN_NUMBER_TO_INDEX_MAP, pins, value)
    
    @classmethod
    def map_pins_to_value(cls, pins: list[int], value: int) -> int:
        return cls._map_pins_to_value(cls.PIN_NUMBER_TO_INDEX_MAP, pins, value)