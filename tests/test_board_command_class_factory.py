"""Tests for IC Utilities"""

# pylint: disable=wrong-import-position,wrong-import-order

import sys
from typing import Type
sys.path.insert(0, '.') # Make VSCode happy...

from dupicolib.board_fw_version import FWVersionDict, FwVersionTools, FWVersionKeys
from dupicolib.board_command_class_factory import BoardCommandClassFactory
from dupicolib.board_commands import BoardCommands
from dupicolib.board_interfaces.m3_board_commands import M3BoardCommands
import pytest

def test_board_command_class_factory_M3(valid_semver_complete):
    fw_ver_dict:FWVersionDict = FwVersionTools.parse(valid_semver_complete)
    
    cmd_class: Type[BoardCommands] = BoardCommandClassFactory.get_command_class(3, fw_ver_dict)
    assert type(cmd_class) == type(M3BoardCommands)

def test_board_command_class_factory_invalid(valid_semver_complete):
    fw_ver_dict:FWVersionDict = FwVersionTools.parse(valid_semver_complete)
    
    with pytest.raises(Exception):
        BoardCommandClassFactory.get_command_class(0, fw_ver_dict)

