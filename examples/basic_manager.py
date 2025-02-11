import pygame

from game_state import State, StateManager
from game_state.errors import ExitGame, ExitState

pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")


GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class FirstScreen(State):
    def run(self) -> None:
        # The run function executes as soon as the state has been changed to it.

        while True:
            # Our game-loop

            self.window.fill(GREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Upon quitting, we raise the ExitGame which we handle outside.

                    self.manager.exit_game()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    # Check if we're clicking the " c " button.
                    # If the condition is met, we change our screen to "SecondScreen" and update
                    # the state in the manager.

                    self.manager.change_state("SecondScreen")
                    self.manager.update_state()

            pygame.display.update()  # Refreshes the screen


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


def main() -> None:
    screen = pygame.display.set_mode((500, 700))
    # Create a basic 500x700 pixel window

    state_manager = StateManager(screen)
    state_manager.load_states(FirstScreen, SecondScreen)
    # We pass in all the screens that we want to use in our game / app.

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
            print(f"State has changed from: {last_state} to {current_state}")


if __name__ == "__main__":
    try:
        main()
    except ExitGame:
        print("Game has exited successfully")
