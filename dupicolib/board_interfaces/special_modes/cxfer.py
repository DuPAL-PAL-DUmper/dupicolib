"""Code to support the CXFER transfer modes"""

from enum import Enum
import logging
import struct
from typing import Callable, final

import serial

from dupicolib.board_utilities import BoardUtilities

_LOGGER = logging.getLogger(__name__)

@final
class CXFERTransfer:
    _XMIT_BLOCK_SIZE: int = 1024
    _XFER_RESPONSE_SIZE: int = 4
    _XFER_CHECKSUM_SIZE: int = 2

    class CXFERSubCommand(Enum):
        SET_ADDR_MAP_0 = 0x00
        SET_ADDR_MAP_1 = 0x01
        SET_ADDR_MAP_2 = 0x02
        SET_ADDR_MAP_3 = 0x03
        SET_DATA_MAP_0 = 0x10
        SET_DATA_MAP_1 = 0x11
        SET_DATA_MAP_2 = 0x12
        SET_DATA_MAP_3 = 0x13
        SET_HI_OUT_MASK = 0xE0
        SET_DATA_MASK = 0xE1
        SET_ADDR_WIDTH = 0xE2
        SET_DATA_WIDTH = 0xE3
        CLEAR = 0xF0
        EXECUTE_READ = 0xFF

    class CXFERResponse(Enum):
        XFER_PKT_START = 0xDEADBEEF
        XFER_PKT_FAIL = 0xBAADF00D
        XFER_DONE = 0xC00FFFEE

    @classmethod
    def read(cls, command_code: int, ser: serial.Serial, update_callback: Callable[[int], None] | None = None) -> bytes | None:
        file_data: bytearray = bytearray()
        data_block: bytearray
        resp: int

        # Start the transfer!
        BoardUtilities.send_binary_command(ser, bytes([command_code, cls.CXFERSubCommand.EXECUTE_READ.value, *([0] * 16)]), 0)

        while True:
            data: bytes = ser.read(cls._XFER_RESPONSE_SIZE)

            if (data_len := len(data)) != cls._XFER_RESPONSE_SIZE:
                raise IOError(f'Received {data_len} data for starting block!')
            
            resp, = struct.unpack('>I', data)

            if resp == cls.CXFERResponse.XFER_PKT_START.value:
                _LOGGER.debug(f'Received a XFER_PKT_START packet, current file size {len(file_data)}')
            elif resp == cls.CXFERResponse.XFER_DONE.value:
                _LOGGER.info(f'Received a XFER_DONE packet, current file size {len(file_data)}')
                break
            else:
                raise IOError(f'Received {resp:0{4}X} while expecting a start block.')
            
            data_block = bytearray()
            rem_data: int = cls._XMIT_BLOCK_SIZE

            while rem_data > 0:
                data = ser.read(16)

                if (data_len := len(data)) <= 0:
                    raise IOError('Timed out while waiting to read data...')
                
                rem_data = rem_data - data_len
                data_block.extend(data)

            calc_checksum: int = BoardUtilities.cxfer_checksum_calculator(bytes(data_block))
            data = ser.read(cls._XFER_CHECKSUM_SIZE)
            if (data_len := len(data)) != cls._XFER_CHECKSUM_SIZE:
                raise IOError(f'Received {data_len} data for checksum!')
            resp, = struct.unpack('<H', data)

            if resp != calc_checksum:
                raise IOError(f'Calculated checksum is {calc_checksum:0{4}X}, received is {resp:0{4}X}')
            
            # Append the block data to the file buffer
            file_data.extend(data_block)

            # Once verified, send the checksum back
            ser.write(data) 

            if update_callback:
                update_callback(len(file_data))
            
        return bytes(file_data)