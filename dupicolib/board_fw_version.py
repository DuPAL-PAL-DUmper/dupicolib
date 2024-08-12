"""This module contains code that handles version strings of the board firmware"""

from typing import final, Optional, TypedDict, Pattern, Match
from enum import Enum
import re

class FWVersionKeys(Enum):
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
    PREREL = 'prerelease'
    BLDMETA = 'buildmetadata'


class FWVersionDict(TypedDict):
    major: str
    minor: str
    patch: str
    prerelease: Optional[str]
    buildmetadata: Optional[str]

@final
class FwVersionTools:
    _REGEX: Pattern = re.compile(f'^(?P<{FWVersionKeys.MAJOR.value}>0|[1-9]\\d*)\\.(?P<{FWVersionKeys.MINOR.value}>0|[1-9]\\d*)\\.(?P<{FWVersionKeys.PATCH.value}>0|[1-9]\\d*)(?:-(?P<{FWVersionKeys.PREREL.value}>(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+(?P<{FWVersionKeys.BLDMETA.value}>[0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$')

    @classmethod
    def parse(cls, ver: str) -> FWVersionDict:
        match: Match[str] | None = cls._REGEX.match(ver.strip())
        if match is None:
            raise ValueError(f'Version string {ver} is not in correct format')
        
        return match.groupdict(default=None) # type: ignore
