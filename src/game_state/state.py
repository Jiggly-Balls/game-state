from __future__ import annotations

import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_state.manager import StateManager


class State:
    window: Optional[pygame.Surface] = None
    manager: Optional[StateManager] = None

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def setup(self) -> None:
        """This method is only called once before `State.run`, i.e right after the class
        has been instantiated inside the StateManager. This method will never be called
        ever again when changing / resetting States.
        """

    def run(self) -> None:
        """The main game loop method to be executed by the StateManager."""
