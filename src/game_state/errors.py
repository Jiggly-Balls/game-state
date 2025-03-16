from __future__ import annotations

from typing import TYPE_CHECKING
from game_state.state import State

if TYPE_CHECKING:
    from typing import Optional, Any


class BaseError(Exception):
    r"""The base class to all game-state errors."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args)

        self.last_state = last_state
        for key, value in kwargs.items():
            setattr(self, key, value)


class StateError(BaseError):
    r"""Raised when an operation is done over an invalid state."""


class StateLoadError(BaseError):
    r"""Raised when an error occurs in loading / unloading a state."""


class ExitState(BaseError):
    r"""An error class used to exit the current state."""


class ExitGame(BaseError):
    r"""An error class used to exit out of the game"""
