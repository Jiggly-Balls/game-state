from typing import Any

import pygame
from game_state import State

GREEN = (0, 255, 0)


class ScreenOne(State, state_name="FirstScreen"):
    def process_event(self, event: pygame.event.Event) -> None:
        # This is executed in our our game loop for every event.

        if event.type == pygame.QUIT:
            # We set the state manager's is_running variable to false
            # which stops the game loop from continuing.
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            # Check if we're clicking the " c " button.
            # If the condition is met, we change our screen to
            # "SecondScreen" in the manager.

            self.manager.change_state("SecondScreen")

    def process_update(self, dt: float) -> None:  # pyright:ignore[reportIncompatibleMethodOverride]
        # This is executed in our game loop.

        self.window.fill(GREEN)
        pygame.display.update()


def hook(**kwargs: Any) -> None:
    # This function should be present below the State you want to load and should call
    # the `StateManager.load_states` method while passing in the State you want to laod
    ScreenOne.manager.load_states(ScreenOne, **kwargs)
