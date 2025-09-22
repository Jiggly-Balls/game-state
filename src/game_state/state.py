from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from .utils import MISSING

if TYPE_CHECKING:
    from typing import Any, Optional

    from pygame import Surface
    from pygame.event import Event

    from .manager import StateManager


__all__ = ("State",)


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

    state_name: str = MISSING
    window: Surface = MISSING
    manager: StateManager = MISSING

    def __init_subclass__(cls, *, state_name: Optional[str] = None) -> None:
        cls.state_name = state_name or cls.__name__

    def on_setup(self) -> None:
        r"""This listener is only called once while being loaded into the ``StateManager``.
        This is also called when reloading the State.

        .. warning::
            This method need not be called manually.

        """
        pass

    def on_enter(self, prevous_state: Optional[State]) -> None:
        r"""This listener is called once when a state has been switched and is
        entering the current state.

        .. warning::
            This method need not be called manually.

        :param prevous_state:
            | The state that was running previously. If there are no previous states,
            | ``None`` is passed
        """
        pass

    def on_leave(self, next_state: State) -> None:
        r"""This listener is called once when the state has been switched and is exiting
        the current one.

        .. warning::
            This method need not be called manually.

        :param next_state:
            | The next state that is going to be applied.
        """
        pass

    def process_event(self, event: Event) -> None:
        r"""To be called when a pygame event needs to be processed.

        .. note::
            This method needs to be called manually.

        :param event:
            | The pygame event object.
        """
        pass

    def process_update(self, *args: Any) -> None:
        r"""The main game loop method to be executed by the ``StateManager``.

        .. note::
            This method needs to be called manually.

        :param \*args:
            | The arguments to be passed on to the update counter.
        """
        pass
