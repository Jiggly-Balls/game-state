"""
Game-State Manager
~~~~~~~~~~~~~~~~~~

A utility package for pygame to manage multiple screens.

:copyright: (c) 2024-present Krish Mohan M.
:license: MIT, see LICENSE for more details.

"""

__version__ = "2.3.0"
__title__ = "game-state"
__author__ = "Krish Mohan M."
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Krish Mohan M."

from typing import Literal, NamedTuple

from .manager import StateManager
from .state import State

__all__ = ("State", "StateManager", "version_info")


class VersionInfo(NamedTuple):
    major: str
    minor: str
    patch: str
    releaselevel: Literal["alpha", "beta", "final"]


def _expand() -> VersionInfo:
    v = __version__.split(".")
    level_types: dict[str, Literal["alpha", "beta"]] = {
        "a": "alpha",
        "b": "beta",
    }
    level = level_types.get(v[-1]) or "final"
    return VersionInfo(major=v[0], minor=v[1], patch=v[2], releaselevel=level)


version_info: VersionInfo = _expand()
