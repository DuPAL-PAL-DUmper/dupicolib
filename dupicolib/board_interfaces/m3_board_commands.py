"""This module contains higher-level code for board interfacing"""

from typing import Dict, List, Tuple, final
from enum import Enum

import serial

from dupicolib.board_utilities import BoardUtilities
from dupicolib.board_commands import BoardCommands

class CommandCode(Enum):
    EXTENDED_WRITE = 'E'
    WRITE = 'W'
    READ = 'R'
    RESET = 'K'
    POWER = 'P'
    TEST = 'T'

@final
class M3BoardCommands(BoardCommands):
    # The following map is used to associate a pin number (e.g. pin 1 or 10) on the socket
    # with the corresponding bit index used to access said pin by the dupico.
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
        41: 39
    } 

    @staticmethod
    def test_board(ser: serial.Serial) -> bool | None:
        """Perform a minimal self-test of the board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            bool | None: True if test passed correctly, False otherwise
        """        
        res: str | None = BoardUtilities.send_command(ser, CommandCode.TEST.value)

        if res and len(res) == 3 and res[0] == CommandCode.TEST.value:
            return int(res[2:]) == 1
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
        res: str | None = BoardUtilities.send_command(ser, CommandCode.POWER.value, ['1' if state else '0'])

        if res and len(res) == 3 and res[0] == CommandCode.POWER.value:
            return int(res[2:]) == 1
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
        # Format the parameter as a 16 chars hex string
        res: str | None = BoardUtilities.send_command(ser, CommandCode.WRITE.value, [f'{pins:0{16}X}'])

        if res and len(res) == 18 and res[0] == CommandCode.WRITE.value:
            return int(res[2:], 16)
        else:
            return None
        
    @staticmethod
    def write_pins_extended(ser: serial.Serial, pins_list: Tuple[int]) -> List[int] | None:
        """Write pins extended, to send multiple write commands with a single string

        Args:
            ser (serial.Serial): serial port on which to send the command
            pins_list (Tuple[int]): tuple of writes to be performed, already remapped

        Returns:
            List[int] | None: List of responses for every requested write, or None if the request failed
        """        
        wre_responses: List[int] = []
        ser.write(BoardUtilities.build_command(CommandCode.EXTENDED_WRITE.value, [f'{entry:0{16}X}' for entry in pins_list]))

        for _ in range(0, len(pins_list)):
            response = BoardUtilities.read_response_string(ser)
            if response is None or len(response) != 18 or response[0] != CommandCode.WRITE.value: # Something went wrong...
                return None
            wre_responses.append(int(response[2:], 16))

        return wre_responses
        
    @staticmethod
    def read_pins(ser: serial.Serial) -> int | None:
        """Read the value of the pins

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """        
        res: str | None = BoardUtilities.send_command(ser, CommandCode.READ.value)

        if res and len(res) == 18 and res[0] == CommandCode.READ.value:
            return int(res[2:], 16)
        else:
            return None
        
    @classmethod
    def map_value_to_pins(cls, pins: list[int], value: int) -> int:
        return cls._map_value_to_pins(cls.PIN_NUMBER_TO_INDEX_MAP, pins, value)
    
    @classmethod
    def map_pins_to_value(cls, pins: list[int], value: int) -> int:
        return cls._map_pins_to_value(cls.PIN_NUMBER_TO_INDEX_MAP, pins, value)