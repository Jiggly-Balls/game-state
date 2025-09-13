import pygame
from game_state import State, StateManager

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
speed = 100
pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")


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


class ScreenTwo(State, state_name="SecondScreen"):
    def __init__(self) -> None:
        self.player_x: float = 250.0

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            # Check if we're clicking the " c " button.
            # If the condition is met, we change our screen to
            # "FirstScreen" in the manager.

            self.manager.change_state("FirstScreen")

    def process_update(self, dt: float) -> None:  # pyright:ignore[reportIncompatibleMethodOverride]
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
    screen = pygame.display.set_mode((500, 700))
    # Create a basic 500x700 pixel window

    state_manager = StateManager(screen)
    state_manager.load_states(ScreenOne, ScreenTwo)
    # We pass in all the screens that we want to use in our game / app.

    state_manager.change_state("FirstScreen")
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
