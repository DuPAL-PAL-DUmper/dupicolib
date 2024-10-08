"""This module is an abstract class to set the shape for classes providing higher-level interface to hardware boards"""

from enum import Enum
from typing import Dict

import serial

from dupicolib.board_commands_interface import BoardCommandsInterface
from dupicolib.board_utilities import BoardUtilities

class CommandCode(Enum):
    MODEL = 4
    VERSION = 6

class HardwareBoardCommands(BoardCommandsInterface):
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
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.MODEL.value]), 1)

        if res is not None:
            return res[0]
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
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.VERSION.value]), 10)

        if res is not None:
            return res.decode(encoding='ASCII').rstrip('\x00').strip() # Clear the terminating NULLs
        else:
            return None

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
            pin_pos: int = map[pin]
            if (value & (1 << idx)) and (pin_pos >= 0):
                ret_val = ret_val | (1 << pin_pos)

        return ret_val

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
            pin_pos: int = map[pin]
            if (pin_pos >= 0) and (value & (1 << pin_pos)):
                ret_val = ret_val | (1 << idx)

        return ret_val