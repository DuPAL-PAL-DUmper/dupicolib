"""Tests for Board Utilities"""

from dupicolib.board_utilities import BoardUtilities

# pylint: disable=wrong-import-position,wrong-import-order

import sys
sys.path.insert(0, '.') # Make VSCode happy...

import pytest

def test_command_checksum_calculator(valid_semver_complete):
    """Execute a checksum calculation"""
    assert BoardUtilities.command_checksum_calculator(bytes([4])) == 252
    assert BoardUtilities.command_checksum_calculator(bytes([4, 252])) == 0

def test_cxfer_checksum_calculator(valid_semver_complete):
    """Execute a 16 bit checksum calculation"""
    assert BoardUtilities.cxfer_checksum_calculator(bytes([4])) == 4
    assert BoardUtilities.cxfer_checksum_calculator(bytes([4, 252])) == 256
