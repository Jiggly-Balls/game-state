from game_state import State, StateManager
from game_state.utils import MISSING


# Classes that we want all our states to share-


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y


class Window:
    def __init__(self, height: int, width: int) -> None:
        self.height: int = height
        self.width: int = width


###############################################

# Setting up our custom state and manager classes to accept custom data-


class CustomBaseState(State["CustomManager"]):
    player: Player = MISSING
    screen: Window = MISSING


class CustomManager(StateManager["CustomBaseState"]):
    def __init__(self, player: Player, screen: Window) -> None:
        super().__init__(bound_state_type=CustomBaseState)

        CustomBaseState.player = player
        CustomBaseState.screen = screen


###############################################

# Using our custom state and manager-


class PauseMenu(CustomBaseState):
    def on_load(self, reload: bool) -> None:
        print()
        print(f"{self.state_name}: {self.player}")
        print(f"{self.state_name}: {self.screen}")


class Game(CustomBaseState):
    def on_load(self, reload: bool) -> None:
        print()
        print(f"{self.state_name}: {self.player}")
        print(f"{self.state_name}: {self.screen}")


class MainMenu(CustomBaseState):
    def on_load(self, reload: bool) -> None:
        print()
        print(f"{self.state_name}: {self.player}")
        print(f"{self.state_name}: {self.screen}")


###############################################

# Initializing our data and loading the states to the manager-

my_player = Player(20, 10)
my_screen = Window(200, 200)
manager = CustomManager(my_player, my_screen)
manager.load_states(MainMenu, Game, PauseMenu)

###############################################
