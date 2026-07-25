import pygame
from game_state import State, StateManager
from game_state.utils import MISSING

pygame.init()
pygame.display.init()
pygame.display.set_caption("Overlay States Example")


class MyBaseState(State["MyBaseState"]):
    # Attributes we want all our states to share.
    screen: pygame.Surface = MISSING


class GameState(MyBaseState, state_name="Game"):
    def __init__(self) -> None:
        self.player_x: float = 250.0
        self.speed: int = 200

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # When the player presses ESC, the manager opens a new overlay
            # state. The current state preserves it's context when you switch
            # back and forth from an overlay state.
            # Over here, since we do not provide any `state_id` argument, the
            # state manager creates and assigns the `PauseState` a unique integer.

            self.manager.open_overlay("Pause")

    def process_update(self, dt: float) -> None:
        self.screen.fill((0, 0, 255))

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.player_x -= self.speed * dt
        if pressed[pygame.K_d]:
            self.player_x += self.speed * dt

        pygame.draw.rect(self.screen, "red", (self.player_x, 100, 50, 50))


class PauseState(MyBaseState, state_name="Pause"):
    def __init__(self) -> None:
        self.frame_snap: None | pygame.Surface = None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.manager.is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Closing the overlay hands control straight back to GameState,
            # right where the player left off.
            # The state automatically gets assigned a `state_id` which we or
            # the state manager created when calling `open_overlay` method.
            self.manager.close_overlay(self.state_id)

    def on_overlay_open(self, temporary: bool) -> None:
        # This is called right when we call `StateManager.open_overlay`
        if self.frame_snap is None:
            self.frame_snap = self.screen.copy()
            self.frame_snap.fill(
                (100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT
            )

    def on_overlay_close(self, temporary: bool) -> None:
        # This is called when either `StateManager.close_overlay` or `StateManager.close_all_overlays` fires.
        self.frame_snap = None

    def process_update(self, dt: float) -> None:
        pygame.draw.rect(self.frame_snap, "green", (100, 200, 300, 200))
        self.screen.blit(self.frame_snap, (0, 0))


def main() -> None:
    screen = pygame.display.set_mode((500, 600))

    state_manager = StateManager(bound_state_type=MyBaseState, screen=screen)
    state_manager.load_states(GameState, PauseState)
    state_manager.change_state("Game")

    clock = pygame.time.Clock()

    while state_manager.is_running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            state_manager.current_state.process_event(event)

        state_manager.current_state.process_update(dt)
        pygame.display.update()


if __name__ == "__main__":
    main()
