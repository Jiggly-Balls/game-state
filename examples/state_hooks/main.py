from pathlib import Path
from typing import Any

import pygame
from game_state import State, StateManager

pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Hooks Example")


def main() -> None:
    screen = pygame.display.set_mode((500, 600))
    # Create a basic 500x600 pixel window

    state_manager = StateManager[State[Any]](screen)

    path_obj = Path("states.")

    # Use glob to find all files ending with .py
    for file_path in path_obj.glob("*.py"):
        if file_path.is_file():  # Ensure it's a file and not a directory
            state_manager.connect_state_hook("states." + file_path.name[:-3])

    # The other alternative-
    # state_manager.connect_state_hook("main_menu")
    # state_manager.connect_state_hook("game")

    state_manager.change_state("MainMenu")
    # We need to use the name we supplied in the __init_sublcass__'s `state_name`.
    # If no state_name was passed, we use the class name itself.

    clock = pygame.time.Clock()

    assert state_manager.current_state is not None

    while state_manager.is_running:
        # The state manager has a `is_running` attribute which is `True` by default

        dt = (
            clock.tick(60) / 1000
        )  # The delta time from the clock for frame rate independance.

        for event in pygame.event.get():
            state_manager.current_state.process_event(event)
            # Calling the event function of the running state.

        state_manager.current_state.process_update(dt)
        # Calling the update function of the running state.


if __name__ == "__main__":
    main()
