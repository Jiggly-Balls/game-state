import pygame

from game_state import State
from game_state.utils import MISSING


class MyBaseState(State["MyBaseState"]):
    window: pygame.Surface = MISSING

    def process_event(self, event: pygame.event.Event) -> None:
        pass

    def process_update(self, dt: float) -> None:
        pass
