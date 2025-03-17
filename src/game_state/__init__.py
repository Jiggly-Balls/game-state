"""
Game-State Manager
~~~~~~~~~~~~~~~~~~

A utility package for pygame to manage multiple screens.

:copyright: (c) 2024-present Jiggly-Balls
:license: MIT, see LICENSE for more details.

"""

__version__ = "1.1.1"
__title__ = "game-state"
__author__ = "Jiggly-Balls"
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Jiggly Balls"

from game_state.manager import StateManager
from game_state.state import State
from typing import NamedTuple, Literal

__all__ = ("State", "StateManager")


class VersionInfo(NamedTuple):
    major: str
    minor: str
    patch: str
    releaselevel: Literal["alpha", "beta", "final"]


def _expand() -> VersionInfo:
    v = __version__.split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level = level_types.get(v[-1], "final")
    return VersionInfo(major=v[0], minor=v[1], patch=v[2], releaselevel=level)


version_info: VersionInfo = _expand()
