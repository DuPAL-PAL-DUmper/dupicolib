"""Tests for Board Utilities"""

from dupicolib.board_utilities import BoardUtilities

# pylint: disable=wrong-import-position,wrong-import-order

import sys
sys.path.insert(0, '.') # Make VSCode happy...

import pytest

def test_checksum_calculator(valid_semver_complete):
    """Execute a checksum calculation"""
    assert BoardUtilities._checksum_calculator(bytes([4])) == 252
    assert BoardUtilities._checksum_calculator(bytes([4, 252])) == 0
