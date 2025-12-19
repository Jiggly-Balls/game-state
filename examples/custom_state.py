import pygame

from game_state import State, StateManager
from game_state.utils import MISSING


GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
speed = 200
pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")

# Classes that we want all our states to share-


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y


###############################################


# Setting up our custom state and manager classes to accept custom data-


class CustomBaseState(State["CustomBaseState"]):
    player: Player = MISSING
    screen: pygame.Surface = MISSING

    def process_event(self, event: pygame.event.Event) -> None:
        pass

    def process_update(self, dt: float) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        pass


###############################################

# Using our custom state-


class GameState(CustomBaseState, state_name="Game"):
    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # Check if we're clicking the " w " button.
            # If the condition is met, we change our screen to the
            # "MainMenu" screen from the manager.

            self.manager.change_state("MainMenu")

    def process_update(self, dt: float) -> None:
        self.screen.fill(BLUE)

        # Player movement-
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.player.x -= speed * dt

        if pressed[pygame.K_d]:
            self.player.x += speed * dt

        pygame.draw.rect(
            self.screen,
            "red",
            (
                self.player.x,
                100,
                50,
                50,
            ),
        )
        pygame.display.update()


class MainMenuState(CustomBaseState, state_name="MainMenu"):
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

    def process_update(self, dt: float) -> None:
        # This is executed in our game loop.

        self.screen.fill(GREEN)
        pygame.display.update()


###############################################


def main() -> None:
    my_player = Player(20, 10)
    screen = pygame.display.set_mode((500, 600))

    state_manager = StateManager(
        bound_state_type=CustomBaseState, player=my_player, screen=screen
    )
    # `bound_state_type` accepts our new base state class (CustomBaseState).
    # A base state is a class from which all our actual state implementation
    # subclasses from. Normally our states subclasses from `game_state.State`
    # but we can extend the functionality of it by creating our own base state
    # and using that as the parent class
    #
    # StateManager also allows you to pass in any kwargs which then gets passed
    # in to bound_state_type's class attributes.

    state_manager.load_states(GameState, MainMenuState)
    state_manager.change_state("MainMenu")

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
