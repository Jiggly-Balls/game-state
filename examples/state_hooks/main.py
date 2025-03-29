import pygame

from game_state import StateManager
from game_state.errors import ExitGame, ExitState

pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Hooks Example")


def main() -> None:
    screen = pygame.display.set_mode((500, 700))
    # Create a basic 500x700 pixel window

    state_manager = StateManager(screen)

    state_manager.connect_state_hook("game")
    state_manager.connect_state_hook("menu")

    # The StateManager.connect_state_hook takes in a file path in a similar fashion
    # to how regular python import statements work. If the state files were in a
    # 'states/' folder, you would pass in the argument to the `.connect_state_hook`
    # as 'state_manager.connect_state_hook("states.menu")'.

    state_manager.change_state("FirstScreen")
    # Updates the current state to the desired state (screen) we want.

    while True:
        try:
            state_manager.run_state()
            # This is the entry point of our screen manager.
            # This should only be called once at start up.

        except ExitState as error:
            # Stuff you can do right after a state (screen) has been changed
            # i.e. Save player data, pause / resume / change music, etc...

            last_state = error.last_state
            current_state = state_manager.get_current_state()
            print(
                f"State has changed from: {last_state.state_name} to {current_state.state_name}"
            )


if __name__ == "__main__":
    try:
        main()
    except ExitGame:
        print("Game has exited successfully")
