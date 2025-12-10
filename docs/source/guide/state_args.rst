State Args
==========

``game_state.utils.StateArgs`` provides a convenient way to supply constructor
arguments to states when calling ``StateManager.load_states`` or
``StateManager.add_lazy_states``. The arguments you define in StateArgs are
automatically passed to the state's ``__init__`` method.

A simple example demonstrating state args-

.. code-block:: python

  from game_state import State, StateManager
  from game_state.utils import StateArgs


  class Game(State):
      def __init__(self, player_pos: tuple[int, int]) -> None:
          self.player_pos = player_pos

      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
          print(f"Player position: {self.player_pos}\n")


  class MainMenu(State):
      def __init__(self, bg_colour: str) -> None:
          self.bg_colour = bg_colour

      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
          print(f"Background colour: {self.bg_colour}")


  main_menu_args = StateArgs(state_name="MainMenu", bg_colour="green")
  game_args = StateArgs(state_name="Game", player_pos=(10, 20))

  manager = StateManager(...)  # ... is a placeholder instead of our actual screen.
  manager.load_states(Game, MainMenu, state_args=[main_menu_args, game_args])

Upon running this program, we will get the following output-

.. code-block::

  Game state has been setup!
  Player position: (10, 20)

  MainMenu state has been setup!
  Background colour: green

You can take a look at the `github examples <https://github.com/Jiggly-Balls/game-state/blob/main/examples/state_args.py>`_
for a more complete example.