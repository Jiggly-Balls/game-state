from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional

    from pygame import Surface
    from pygame.event import Event

    from .manager import StateManager


class State(ABC):
    """The State class which works as an individual screen.

    :attributes:
        state_name: :class:`str`
            The name of the state. Has to be unique among other states.
        window: :class:`pygame.Surface`
            The main game window.
        manager: :class:`StateManager`
            The manager to which the state is binded to.
    """

    state_name: str = None
    window: Optional[Surface] = None
    manager: Optional[StateManager] = None

    def __init_subclass__(cls, *, state_name: Optional[str] = None) -> None:
        cls.state_name = state_name or cls.__name__

    def on_setup(self) -> None:
        """This method is only called once while being loaded into the `StateManager`.
        This is also called when reloading the State.
        This method should not be called manually.
        """
        pass

    def on_event(self, event: Event) -> None:
        """To be called when a pygame event needs to be processed."""
        pass

    def on_enter(self, prevous_state: State) -> None:
        """This method is called once when a state has been switched and is
        entering the current state."""
        pass

    def on_update(self, *args: Any) -> None:
        """The main game loop method to be executed by the ``StateManager``."""
        pass

    def on_leave(self, next_state: State) -> None:
        """This method is called once when the state has been switched and is exiting
        the current one"""
        pass
