"""Tests for IC Utilities"""

# pylint: disable=wrong-import-position,wrong-import-order

import sys
sys.path.insert(0, '.') # Make VSCode happy...

from dupicolib.board_fw_version import FWVersionDict, FwVersionTools, FWVersionKeys
import pytest

def test_version_parsing_complete(valid_semver_complete):
    """Test parsing of a complete semver"""
    ver_dict: FWVersionDict = FwVersionTools.parse(valid_semver_complete)
    assert ver_dict[FWVersionKeys.MAJOR.value] == '0'
    assert ver_dict[FWVersionKeys.MINOR.value] == '1'
    assert ver_dict[FWVersionKeys.PATCH.value] == '2'
    assert ver_dict[FWVersionKeys.PREREL.value] == 'abc'
    assert ver_dict[FWVersionKeys.BLDMETA.value] == 'bcd'

def test_version_parsing_valid_limited(valid_semver_limited):
    """Test parsing of a correct semver missing prerelease and build metadata"""
    ver_dict: FWVersionDict = FwVersionTools.parse(valid_semver_limited)
    assert ver_dict[FWVersionKeys.MAJOR.value] == '0'
    assert ver_dict[FWVersionKeys.MINOR.value] == '1'
    assert ver_dict[FWVersionKeys.PATCH.value] == '2'
    assert ver_dict[FWVersionKeys.PREREL.value] is None
    assert ver_dict[FWVersionKeys.BLDMETA.value] is None

def test_version_parsing_invalid_semver_a(invalid_semver_a, invalid_semver_b, invalid_semver_c):
    """Test parsing of broken semver strings"""
    with pytest.raises(ValueError):
        FwVersionTools.parse(invalid_semver_a)

    with pytest.raises(ValueError):
        FwVersionTools.parse(invalid_semver_b)

    with pytest.raises(ValueError):
        FwVersionTools.parse(invalid_semver_c)
