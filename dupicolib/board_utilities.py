"""This module contains low level utility code to communicate with the board"""

from typing import final
from functools import reduce
import operator
import logging
import time

import serial

from dupicolib.board_interfaces.command_structures import CommandTokens

@final
class BoardUtilities:
    """
    This class contains basic utilities for board access.
    """

    _MAX_RESPONSE_SIZE: int = 32
    _ENCODING: str = 'ASCII'

    _BINARY_COMMAND_RESPONSE_FLAG: int = 0x80

    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def _connection_string_loop_check(cls, ser: serial.Serial, retries: int) -> bool:
        for i in range(1, retries + 1):
            # Reset the connection to the board
            ser.dtr = False
            # Clear everything we have up to now
            ser.reset_input_buffer()
            time.sleep(0.5)
            ser.dtr = True
            time.sleep(0.5)

            response = ser.readline(cls._MAX_RESPONSE_SIZE).decode(cls._ENCODING).strip()
            if response and response == CommandTokens.BOARD_ENABLED.value:
                cls._LOGGER.debug(f'Connection try {i} succeeded!')
                return True
            cls._LOGGER.debug(f'Connection try {i} failed, got "{response}"!')     

        return False   

    @classmethod
    def initialize_connection(cls, ser: serial.Serial, retries: int = 2) -> bool:
        """This method toggles DTR and checks that the connection to the board is established by waiting for
        a specific string to be received.
        This string is sent by the board as soon as it detects a new connection.

        If this string is received, this function sets the board to binary protocol mode.

        Args:
            ser (serial.Serial): Serial port connected to the dupico
            retries (int, optional): Number of retries used to check for the string. Defaults to 2.

        Returns:
            bool: True if the connection is validated and board set to the proper protocol.
        """        

        cls._LOGGER.debug('Attempting to detect board...')

        if(cls._connection_string_loop_check(ser, retries)):
            ser.reset_input_buffer()
            return True
    
        cls._LOGGER.critical('Detection attempt failed.')

        return False

    @classmethod
    def send_binary_command(cls, ser: serial.Serial, cmd: bytes, resp_data_len: int) -> bytes | None:
        chks: int = cls._checksum_calculator(cmd)

        ser.write(bytes([*cmd, chks]))

        expected_resp = cmd[0] | cls._BINARY_COMMAND_RESPONSE_FLAG
        resp_code: bytes = ser.read(1)
        if (len(resp_code) != 1 or resp_code[0] != expected_resp):
            cls._LOGGER.error(f'Got response {resp_code[0]:0{2}X} while expected was {expected_resp:0{2}X}')
            ser.reset_input_buffer()
            return None
        
        resp_data = ser.read(resp_data_len + 1) # + 1 as we also need the checksum
        if (len(resp_data) - 1) != resp_data_len:
            cls._LOGGER.error(f'Got response data length {len(resp_data)}, expected was {resp_data_len}')
            ser.reset_input_buffer()
            return None
        
        if cls._checksum_calculator(resp_code + resp_data) != 0:
            cls._LOGGER.error(f'Command has wrong checksum')
            ser.reset_input_buffer()
            return None            
        
        return resp_data[:-1] # Avoid returning the checksum

    @classmethod
    def _checksum_calculator(cls, data: bytes) -> int: 
        return reduce(operator.sub, bytes([0, *data])) & 0xFF
