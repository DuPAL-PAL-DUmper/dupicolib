"""This module contains the tokens for all the supported board commands"""

from enum import Enum
 
class CommandTokens(Enum):
    CMD_ERROR = 'CMD_ERR'
    CMD_START = '>'
    CMD_END = '<'
    RESP_START = '['
    RESP_END = ']'
    BOARD_ENABLED = 'REMOTE_CONTROL_ENABLED'


