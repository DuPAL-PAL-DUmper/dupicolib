"""Fixtures for testing"""

# pylint: disable=wrong-import-position

import sys
sys.path.insert(1, '.') # Make VSCode happy...

import pytest

# Fixtures for pin mapping
@pytest.fixture
def pin_list_8bit() -> list[int]:
    return [1, 2, 3, 4, 10, 20, 22, 41]

@pytest.fixture
def pin_list_18bit() -> list[int]:
    # Taken from a 27C2001, address pins
    return [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 30]

@pytest.fixture
def ignored_pin_list() -> list[int]:
    # Pin list that includes pin 21 and 42 (GND and VCC on model 3) that should be ignored by the remapper
    return [12, 11, 42, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 21]

@pytest.fixture
def invalid_pin_list() -> list[int]:
    # Invalid pin list that includes pin 43 and 44
    return [12, 11, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 43, 44]

# Fixtures for semver checking
@pytest.fixture
def valid_semver_complete() -> str:
    return '0.1.2-abc+bcd'

@pytest.fixture
def valid_semver_limited() -> str:
    return '0.1.2'

@pytest.fixture
def invalid_semver_a() -> str:
    return '1.2-abc+234'

@pytest.fixture
def invalid_semver_b() -> str:
    return '0.1.2-+234'

@pytest.fixture
def invalid_semver_c() -> str:
    return '0.1.2.0-+234'