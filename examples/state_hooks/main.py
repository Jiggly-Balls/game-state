import pygame
from game_state import StateManager

pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Hooks Example")


def main() -> None:
    screen = pygame.display.set_mode((500, 600))
    # Create a basic 500x700 pixel window

    state_manager = StateManager(screen)
    state_manager.connect_state_hook("main_menu")
    state_manager.connect_state_hook("game")
    # We pass in all the screens that we want to use in our game / app.

    state_manager.change_state("MainMenu")
    # We need to use the name we supplied in the __init_sublcass__'s `state_name`.
    # If no state_name was passed, we use the class name itself.

    clock = pygame.time.Clock()

    while state_manager.is_running:
        # The state manager has a `is_running` attribute which is `True` by default

        dt = (
            clock.tick(60) / 1000
        )  # The delta time from the clock for frame rate independance.

        if state_manager.current_state:
            for event in pygame.event.get():
                state_manager.current_state.process_event(event)
                # Calling the event function of the running state.

            state_manager.current_state.process_update(dt)
            # Calling the update function of the running state.


if __name__ == "__main__":
    main()
