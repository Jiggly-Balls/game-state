from typing import Any

import pygame
from game_state import State

BLUE = (0, 0, 255)


class GameState(State, state_name="Game"):
    def __init__(self) -> None:
        self.player_x: float = 250.0
        self.speed = 200

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # Check if we're clicking the " w " button.
            # If the condition is met, we change our screen to the
            # "MainMenu" screen from the manager.

            self.manager.change_state("MainMenu")

    def process_update(self, *args: float) -> None:
        dt = args[0]

        self.window.fill(BLUE)

        # Player movement-
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.player_x -= self.speed * dt

        if pressed[pygame.K_d]:
            self.player_x += self.speed * dt

        pygame.draw.rect(
            self.window,
            "red",
            (
                self.player_x,
                100,
                50,
                50,
            ),
        )

        pygame.display.update()


def hook(**kwargs: Any) -> None:
    # This function should be present below the State you want to load and should call
    # the `StateManager.load_states` method while passing in the State you want to laod
    GameState.manager.load_states(GameState, **kwargs)
