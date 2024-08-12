"""Board command class factory"""

from typing import final, Dict, Type
from collections import defaultdict

from dupicolib.board_commands_interface import BoardCommandsInterface
from dupicolib.board_interfaces.m3_board_commands import M3BoardCommands
from dupicolib.board_fw_version import FWVersionDict, FWVersionKeys
@final
class BoardCommandClassFactory: 
    _COMMAND_CLASS_MAP: Dict[int, Dict[str, Type[BoardCommandsInterface]]] = {
        3: defaultdict(lambda: M3BoardCommands) # We have only one set of commands for M 3 boards, for now
    }

    @classmethod
    def get_command_class(cls, model: int, version: FWVersionDict) -> Type[BoardCommandsInterface]:
        """Return the command class specific for this combination of model and firmware version

        Args:
            model (int): Model of the board
            version (FWVersionDict): Parsed firmware version

        Returns:
            Type[BoardCommands]: subclass of BoardCommands that handle this specific board
        """        
        return cls._COMMAND_CLASS_MAP[model][version[FWVersionKeys.MAJOR.value]]