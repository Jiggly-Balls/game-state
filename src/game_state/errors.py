from __future__ import annotations

from typing import TYPE_CHECKING

from .state import State

if TYPE_CHECKING:
    from typing import Any, Optional


__all__ = ("BaseError", "StateError", "StateLoadError")


class BaseError(Exception):
    r"""The base class to all game-state errors."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args)

        self.last_state: Optional[State] = last_state
        for key, value in kwargs.items():
            setattr(self, key, value)


class StateError(BaseError):
    r"""Raised when an operation is done over an invalid state."""


class StateLoadError(BaseError):
    r"""Raised when an error occurs in loading / unloading a state."""
