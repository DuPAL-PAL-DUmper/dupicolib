"""Tests for IC Utilities"""

# pylint: disable=wrong-import-position,wrong-import-order

import sys
sys.path.insert(0, '.') # Make VSCode happy...

from dupicolib.board_interfaces.m3_board_commands import M3BoardCommands
import pytest

def test_map_value_to_pins_8bit_m3(pin_list_8bit):
    """Test a mapping of a value to specific pins"""
    assert M3BoardCommands.map_value_to_pins(pins=pin_list_8bit, value=0xFF) == 0x800018020F
    assert M3BoardCommands.map_value_to_pins(pins=pin_list_8bit, value=0xAA) == 0x800008000A

def test_map_value_to_pins_18bit_m3(pin_list_18bit):
    """Test a mapping of a value to specific pins"""
    assert M3BoardCommands.map_value_to_pins(pins=pin_list_18bit, value=0x3FFFF) == 0x1FA00FFE
    assert M3BoardCommands.map_value_to_pins(pins=pin_list_18bit, value=0x12345) == 0x7000A22
    
def test_map_pins_to_value_8bit_m3(pin_list_8bit):
    """Test a mapping of data read from pins to original value"""
    assert M3BoardCommands.map_pins_to_value(pins=pin_list_8bit, value=0x800018020F) == 0xFF
    assert M3BoardCommands.map_pins_to_value(pins=pin_list_8bit, value=0x800008000A) == 0xAA

def test_map_pins_to_value_18bit_m3(pin_list_18bit):
    """Test a mapping of data read from pins to original value"""
    assert M3BoardCommands.map_pins_to_value(pins=pin_list_18bit, value=0x1FA00FFE) == 0x3FFFF
    assert M3BoardCommands.map_pins_to_value(pins=pin_list_18bit, value=0x7000A22) == 0x12345

def test_ignored_pins_exc(ignored_pin_list):
    """Tests that no exception is raised if we use ignored pins"""
    assert M3BoardCommands.map_pins_to_value(pins=ignored_pin_list, value=0) == 0

def test_invalid_pins_exc(invalid_pin_list):
    """Tests that an exception is raised if we attempt to use a pin not specified in the map"""
    with pytest.raises(Exception):
        M3BoardCommands.map_pins_to_value(pins=invalid_pin_list, value=0)
