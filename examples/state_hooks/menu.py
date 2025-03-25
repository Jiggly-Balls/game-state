from typing import Any

import pygame

from game_state import State

BLUE = (0, 0, 255)


class SecondScreen(State):
    def run(self) -> None:
        # The exact same thing happens in the SecondScreen except we use a different
        # colour for the screen & we change our current state to FirstScreen if the
        # user presses " c ".

        while True:
            self.window.fill(BLUE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.manager.exit_game()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    self.manager.change_state(
                        "FirstScreen"
                    )  # Change our state to FirstScreen.
                    self.manager.update_state()  # Updates / resets the state.

            pygame.display.update()


def hook(**kwargs: Any) -> None:
    # This function should be present below the State you want to load and should call
    # the `StateManager.load_states` method while passing in the State you want to laod
    SecondScreen.manager.load_states(SecondScreen, **kwargs)
