import pygame
from game_state import State, StateManager
from game_state.utils import StateArgs

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
speed = 200
pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")


class MainMenuState(State, state_name="MainMenu"):
    def __init__(self, bg_colour: tuple[int, int, int]) -> None:
        self.bg_colour = bg_colour

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

        self.window.fill(self.bg_colour)
        pygame.display.update()


class GameState(State, state_name="Game"):
    def __init__(self, player_x: float) -> None:
        self.player_x: float = player_x

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

    # The arguments we want to send to our MainMenuState & GameState constructor.
    # And we pass it to the state_manager.load_states
    main_menu_args = StateArgs(state_name="MainMenu", bg_colour=GREEN)
    game_args = StateArgs(state_name="Game", player_x=250.0)

    state_manager = StateManager(screen)
    state_manager.load_states(
        MainMenuState, GameState, state_args=(main_menu_args, game_args)
    )
    # We pass in all the screens that we want to use in our game / app.

    state_manager.change_state("MainMenu")
    # We need to use the name we supplied in the __init_sublcass__'s `state_name`.
    # If no state_name was passed, we use the class name itself.

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
