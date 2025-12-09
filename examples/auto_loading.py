from game_state import State, StateManager


class Game(State, lazy_load=True):
    def on_setup(self) -> None:
        print(f"{self.state_name} has initialized!")


class MainMenu(State, eager_load=True):
    def on_setup(self) -> None:
        print(f"{self.state_name} has initialized!")


manager = StateManager(...)  # pyright: ignore[reportArgumentType]
manager.add_lazy_states()
manager.load_states()
manager.change_state("Game")
