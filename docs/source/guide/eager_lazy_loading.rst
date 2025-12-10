Eager & Lazy Loading
====================

From version ``2.2`` onwards the library allows you to load states lazily. In
this guide we will take a look at how to load states eagarly and lazily, and
also see their differences.


Eager Loading
-------------

Firstly, what is eagar loading?

So far in the library you can load states into the state manager via
``StateManager.load_states`` method. When calling this method the state manager
immediately loads the state to memory regardless of whether the state was ever
used in the program's life span. In all our previous examples we have been
eagar loading our states.

A mock example of eager loading-

.. code-block:: python

  from game_state import State, StateManager


  class Game(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")


  class MainMenu(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
  
  manager = StateManager(...)  # ... is a placeholder instead of our actual screen.
  manager.load_states(Game, MainMenu)  # Eager loading our states.

By running this code we get the following output-

.. code-block::

  Game state has been setup!
  MainMenu state has been setup!

If you notice, in our code we have never switched to either of those states,
but even so the manager still loads them. The wasted time in loading unused
states can be better spent somewhere else. This is where lazy states can help
our needs.


Lazy Loading
------------

In version ``2.2`` onwards, the library supports a new method called
``StateManager.add_lazy_states``. This method allows us to lazily load states
into the manager. Let's see an example to understand better.

Using the same example as before with a slight change-

.. code-block:: python

  from game_state import State, StateManager


  class Game(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")


  class MainMenu(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
  
  manager = StateManager(...)  # ... is a placeholder instead of our actual screen.
  manager.add_lazy_states(Game, MainMenu)  # Lazy loading our states.

When we run this code, we don't get any output! This is because when you call
``manager.add_lazy_states`` method, the manager only caches those types into
itself. The initialization only occurs when you use the state, via changing to
the state by ``manager.change_state``.

Let's make those changes and observe the output-

.. code-block:: python

  from game_state import State, StateManager


  class Game(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")


  class MainMenu(State):
      def on_setup(self) -> None:
          print(f"{self.state_name} state has been setup!")
  
  manager = StateManager(...)  # ... is a placeholder instead of our actual screen.
  manager.load_states(Game, MainMenu)  # Eager loading our states.

  manager.change_state("MainMenu")  # Initializes the `MainMenu` state.
  manager.change_state("Game")  # Initializes the `Game` state.

Upon running this program we get the following output-

.. code-block::

  MainMenu state has been setup!
  Game state has been setup!


Lazy Loading or Eager Loading? Which one?
-----------------------------------------

Both of these loading methods are useful in their own ways. You can eager load
your states at the start of your program to minimize any load time needed
while switching between states.

On the other hand you can use lazy loading to minimize start up time by only
loading the required states as you progress. One reason can be when you have
a lot of assets to load, you can split the asset loading among their
respective states and load only when necessary.

A combination of eager and lazy loading states can play a huge role in your
app.

You can take a look at the `github examples <https://github.com/Jiggly-Balls/game-state/blob/main/examples/lazy_state_example.py>`_
for a more complete example.