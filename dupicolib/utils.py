"""Miscellaneous utilities used by the library"""

from itertools import zip_longest
from collections.abc import Iterable
from typing import Iterator, Tuple, TypeVar

T = TypeVar('T')


# From https://stackoverflow.com/questions/434287/how-to-iterate-over-a-list-in-chunks
# See https://docs.python.org/3/library/itertools.html#itertools.zip_longest
def iter_grouper(iterable: Iterable[T], group_size: int, fillvalue: T | None = None) -> Iterator[Tuple[T]]:
    # We are feeding multiple copies of the same iterator to zip_longest, so it will consume from the same
    # source when zipping values, resulting in grouping the values
    args = [iter(iterable)] * group_size
    return zip_longest(*args, fillvalue=fillvalue)