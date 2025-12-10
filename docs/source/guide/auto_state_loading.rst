Auto State Loading
==================

From version ``2.2`` onwards, the library supports auto state loading, which
is an alternative way of loading states like the
``StateManager.connect_state_hook``, ``StateManager.load_states`` and 
``StateManager.add_lazy_states``.

In all these methods, you are forced to either import all your states and
load them to your desired load method or pass in paths to where your state
lies. Depending on your taste and codebase, this approach may not look the
cleanest or may look too verbose.

Auto loading of states allow you to load states without the need of importing
or passing in paths of the state files.

.. code-block:: python

  from game_state import State, StateManager


  class Game(State, lazy_load=True):  # loads the state lazily
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")


  class MainMenu(State, eager_load=True):  # Loads the state eagarly
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
  

  manager = StateManager(...)  # ... is a placeholder instead of our actual screen.
  manager.load_states()  # Loads all the eager states.
  manager.add_lazy_states()  # Adds all the lazy states.

Even though we mark our subclasses to ``eager_load`` and ``lazy_load``, we
still need to call the ``manager.load_states`` and ``manager.add_lazy_states``
method.

You can take a look at the `github examples <https://github.com/Jiggly-Balls/game-state/blob/main/examples/auto_loading.py>`_
for a more complete example.
