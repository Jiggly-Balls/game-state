from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Any
    from src.game_state.state import State


class BaseError(Exception):
    """The base class to all custom errors."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args)

        self.last_state = last_state
        for key, value in kwargs.items():
            setattr(self, key, value)


class StateError(BaseError):
    """Raised when an operation is done over an invalid state."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, last_state=last_state, **kwargs)


class StateLoadError(BaseError):
    """Raised when an error occurs in loading / unloading a state."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, last_state=last_state, **kwargs)


class ExitStateError(BaseError):
    """An error class used to exit the current state."""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, last_state=last_state, **kwargs)


class ExitGameError(BaseError):
    """An error class used to exit out of the game"""

    def __init__(
        self, *args: Any, last_state: Optional[State] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, last_state=last_state, **kwargs)
