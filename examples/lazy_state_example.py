import pygame
from game_state import State, StateManager

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
speed = 200
pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")


class MainMenuState(State, state_name="MainMenu"):
    def on_setup(self) -> None:
        print(f"{self.state_name} has initialized!")

    def process_event(self, event: pygame.event.Event) -> None:
        # This is executed in our our game loop for every event.

        if event.type == pygame.QUIT:
            # We set the state manager's is_running variable to false
            # which stops the game loop from continuing.
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # Check if we're clicking the " w " button.
            # If the condition is met, we change our screen to the
            # "Game" screen from the manager.

            self.manager.change_state("Game")

    def process_update(self, *args: float) -> None:
        # This is executed in our game loop.

        self.window.fill(GREEN)
        pygame.display.update()


class GameState(State, state_name="Game"):
    def __init__(self) -> None:
        self.player_x: float = 250.0

    def on_setup(self) -> None:
        print(f"{self.state_name} has initialized!")

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
            self.player_x -= speed * dt

        if pressed[pygame.K_d]:
            self.player_x += speed * dt

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


def main() -> None:
    screen = pygame.display.set_mode((500, 600))
    # Create a basic 500x600 pixel window

    state_manager = StateManager(screen)
    state_manager.add_lazy_states(MainMenuState, GameState)
    # The states that we want to load lazily. Currently it is only cached in the manager.

    state_manager.change_state("MainMenu")
    # Only upon switching to that state, the initialization of it occurs.

    clock = pygame.time.Clock()

    assert state_manager.current_state is not None

    while state_manager.is_running:
        # The state manager has a `is_running` attribute which is `True` by default

        dt = clock.tick(60) / 1000
        # The delta time from the clock for frame rate independance.

        for event in pygame.event.get():
            state_manager.current_state.process_event(event)
            # Calling the event function of the running state.

        state_manager.current_state.process_update(dt)
        # Calling the update function of the running state.


if __name__ == "__main__":
    main()
