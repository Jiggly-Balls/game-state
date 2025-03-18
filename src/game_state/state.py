from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface
    from typing import Optional
    from .manager import StateManager


class State:
    """The State class which works as an individual screen.

    :attributes:
        state_name: :class:`Optional`\[:class:`str`]
            The name of the state. Has to be unique among other states.
        window: :class:`pygame.Surface`
            The main game window.
        manager: :class:`StateManager`
            The manager to which the state is binded to.
        clock: :class:`pygame.time.Clock`
            Pygame's clock.

    :param state_name:
        The name of the state. Has to be unique among other states.
    """

    state_name: Optional[str] = None
    window: Optional[Surface] = None
    manager: Optional[StateManager] = None
    clock = pygame.time.Clock()

    def __init_subclass__(cls, state_name: Optional[str] = None) -> None:
        cls.state_name = state_name or cls.__name__

    def setup(self) -> None:
        """This method is only called once before ``State.run``, i.e right after the class
        has been instantiated inside the StateManager. This method will never be called
        ever again when changing / resetting States.
        """
        pass

    def run(self) -> None:
        """The main game loop method to be executed by the ``StateManager``."""
        pass
