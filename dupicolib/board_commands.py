"""This module is an abstract class to set the shape for classes providing higher-level interface to the boards"""

from enum import Enum
from typing import Dict, List, Tuple
from abc import ABC

import serial

from dupicolib.board_utilities import BoardUtilities

class CommandCode(Enum):
    MODEL = 'M'
    VERSION = 'V'

class BoardCommands(ABC):
    # Model and version command need to be common to every device, so we can gather the information
    # needed to distinguish them from one another
    @staticmethod
    def get_model(ser: serial.Serial) -> int | None:
        """Read the model of the connected board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: Return the model number, or None if the response cannot be read correctly
        """        
        res: str | None = BoardUtilities.send_command(ser, CommandCode.MODEL.value)

        if res and len(res) >= 3 and res[0] == CommandCode.MODEL.value:
            return int(res[2:])
        else:
            return None

    @staticmethod
    def get_version(ser: serial.Serial) -> str | None:
        """Read the version of the firmware on the connected board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            ser | None: Return the version number of the firmware, or None if the response cannot be read correctly
        """        
        res: str | None = BoardUtilities.send_command(ser, CommandCode.VERSION.value)

        if res and len(res) >= 3 and res[0] == CommandCode.VERSION.value:
            return res[2:]
        else:
            return None

    @staticmethod
    def test_board(ser: serial.Serial) -> bool | None:
        """Perform a minimal self-test of the board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            bool | None: True if test passed correctly, False otherwise
        """        
        pass
        
    @staticmethod
    def set_power(ser: serial.Serial, state: bool) -> bool | None:
        """Enable or disable the power on the socket VCC

        Args:
            ser (serial.Serial): serial port on which to send the command
            state (bool): True if we wish power applied, False otherwise

        Returns:
            bool | None: True if power was applied, False otherwise, None in case we did not read the response correctly
        """        
        pass
        
    @staticmethod
    def write_pins(ser: serial.Serial, pins: int) -> int | None:
        """Toggle the specified pins and read their status back

        Args:
            ser (serial.Serial): serial port on which to send the command
            pins (int): value that the pins will be set to. A bit set to '1' means that the pin will be pulled high

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """        
        pass
        
    @staticmethod
    def write_pins_extended(ser: serial.Serial, pins_list: Tuple[int]) -> List[int] | None:
        """Write pins extended, to send multiple write commands with a single string

        Args:
            ser (serial.Serial): serial port on which to send the command
            pins_list (Tuple[int]): tuple of writes to be performed, already remapped

        Returns:
            List[int] | None: List of responses for every requested write, or None if the request failed
        """        
        pass

    @staticmethod
    def read_pins(ser: serial.Serial) -> int | None:
        """Read the value of the pins

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """        
        pass

    @classmethod
    def map_value_to_pins(cls, pins: list[int], value: int) -> int:
        pass

    @staticmethod
    def _map_value_to_pins(map: Dict[int, int], pins: list[int], value: int) -> int:
        """This method takes a number to set on selected pins and uses a list of said pins to
        convert into it into a value that can address those pins

        Args:
            map (Dict[int, int]): dictionary defining the pin map
            pins (list[int]): A list of the pins associated to every bit of the input value (1-index based)
            value (int): The value to map to the pins

        Returns:
            int: A value that can be used by the dupico to address and change the selected pins
        """

        ret_val: int = 0

        for idx, pin in enumerate(pins):
            if value & (1 << idx):
                ret_val = ret_val | (1 << map[pin])

        return ret_val
    
    @classmethod
    def map_pins_to_value(cls, pins: list[int], value: int) -> int:
        pass

    @staticmethod
    def _map_pins_to_value(map: Dict[int, int], pins: list[int], value: int) -> int:
        """This method performs the reverse operation of map_value_to pins: it converts
        a value read from the dupico representing the "addresses" of the pins into a value that
        actually represent the number that those pins compose

        Args:
            map (Dict[int, int]): dictionary defining the pin map
            pins (list[int]): The list of pins associated to the value
            value (int): the value representing the pin state

        Returns:
            int: the actual number that those pins are forming
        """        

        ret_val: int = 0

        for idx, pin in enumerate(pins):
            if value & (1 << map[pin]):
                ret_val = ret_val | (1 << idx)

        return ret_val