"""This module contains low level utility code to communicate with the board"""

from typing import final
import logging

import serial

from dupicolib.board_interfaces.command_structures import CommandTokens

@final
class BoardUtilities:
    """
    This class contains basic utilities for board access.
    """

    _MAX_RESPONSE_SIZE: int = 32
    _ENCODING: str = 'ASCII'

    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def _connection_string_loop_check(cls, ser: serial.Serial, retries: int) -> bool:
        for i in range(1, retries + 1):
            response = ser.readline(cls._MAX_RESPONSE_SIZE).decode(cls._ENCODING).strip()
            if response and response == CommandTokens.BOARD_ENABLED.value:
                cls._LOGGER.debug(f'Connection try {i} succeeded!')
                return True
            cls._LOGGER.debug(f'Connection try {i} failed, got "{response}"!')     

        return False   

    @classmethod
    def check_connection_string(cls, ser: serial.Serial, retries: int = 2) -> bool:
        """This methods check that the connection to the board is established by waiting for
        a specific string to be received. 

        Args:
            ser (serial.Serial): Serial port connected to the dupico
            retries (int, optional): Number of retries used to check for the string. Defaults to 2.

        Returns:
            bool: True if the connection string is found, False if not.
        """        
        response: str

        cls._LOGGER.debug('Attempting connection to board...')

        if(cls._connection_string_loop_check(ser, retries)):
            return True
    
        cls._LOGGER.critical('Connection attempt failed...')

        return False

    @classmethod
    def send_command(cls, ser: serial.Serial, cmd: str, params: list[str] = [], retries: int = 5) -> str | None:
        ser.write(cls.build_command(cmd, params))

        return cls.read_response_string(ser, retries)
    
    @classmethod
    def build_command(cls, cmd: str, params: list[str] = []) -> bytes:
        # If we have entries on the list, we'll use this trick to add a space at the beginning of the parameter list for command generation
        if params:
            params.insert(0, '')

        return f'{CommandTokens.CMD_START.value}{cmd}{' '.join(params)}{CommandTokens.CMD_END.value}'.encode(cls._ENCODING)
    
    @classmethod
    def read_response_string(cls, ser: serial.Serial, retries: int = 5) -> str | None:
        while retries > 0:
            response: str = ser.readline(cls._MAX_RESPONSE_SIZE).decode(cls._ENCODING).strip()

            if len(response) < 3 or response[0] != CommandTokens.RESP_START.value or response[-1] != CommandTokens.RESP_END.value:
                retries = retries - 1
            else:
                return response[1:-1]
        
        return None
