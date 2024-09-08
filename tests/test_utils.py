"""Tests for Utilities"""

# pylint: disable=wrong-import-position,wrong-import-order

import sys
from typing import Tuple
sys.path.insert(0, '.') # Make VSCode happy...

import dupicolib.utils as DPUtils
import pytest

def test_iter_grouper():
    """Test iter_grouper"""
    example_list: list[int] = [0, 1, 2, 3, 4, 5, 6, 7]
    
    grouped_a: list[Tuple[int]] = list(DPUtils.iter_grouper(example_list, 3, fillvalue=255))
    grouped_b: list[Tuple[int]] = list(DPUtils.iter_grouper(example_list, 3))

    assert len(grouped_a) == 3
    assert len(grouped_b) == 3
    
    assert grouped_a == [(0, 1, 2), (3, 4, 5), (6, 7, 255)]
    assert grouped_b == [(0, 1, 2), (3, 4, 5), (6, 7, None)]
