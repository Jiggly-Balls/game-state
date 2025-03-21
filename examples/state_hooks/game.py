import pygame
from game_state import State


GREEN = (0, 255, 0)


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


def hook(**kwargs) -> None:
    # This function should be present below the State you want to load and should call
    # the `StateManager.load_states` method while passing in the State you want to laod
    FirstScreen.manager.load_states(FirstScreen, **kwargs)
