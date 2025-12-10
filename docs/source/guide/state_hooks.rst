State Hooks
===========

State hooks allow you to dynamically load state files without needing to import
them.

Let's take our previous example and split the ``MainMenuState`` and
``GameState`` into separate files and load the file paths instead of importing
their classes.

Let's structure our project like this-

.. admonition:: Our project structure. With ``game_state_hooks`` being the root of the project.
    :class: seealso

    .. code-block::

        game_state_hooks/
            │ - main.py
            │
            └───states/
                │ - game.py
                │ - main_menu.py

Inside our ``main.py`` file let's initialize our pygame and dynamically load
the state files.

.. admonition:: ``main.py`` file
    :class: seealso

    .. code-block:: python

        import pygame
        from game_state import StateManager

        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("Game State Hooks Example")


        def main() -> None:
            screen = pygame.display.set_mode((500, 600))
            # Create a basic 500x600 pixel window

            state_manager = StateManager(screen)
            state_manager.connect_state_hook("states.main_menu")
            state_manager.connect_state_hook("states.game")
            # Here we pass in the path to the state files.

The ``state_manager.connect_state_hook`` method is what calls the hook function
in our state file to load it.

Note that the path must be dot separated like regular Python imports if 
accessing a sub-module. e.g. ``states.game`` if you want to import
``states/game.py``.

We can also automate loading our state files by looping through our ``states/``
directory.

.. admonition:: ``main.py`` file
    :class: seealso

    .. code-block:: python

        import pygame
        from game_state import StateManager
        from pathlib import Path

        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("Game State Hooks Example")


        def main() -> None:
            screen = pygame.display.set_mode((500, 600))
            # Create a basic 500x600 pixel window

            state_manager = StateManager(screen)
            STATES_DIR = "states."
            path_obj = Path(STATES_DIR)

            # Use glob to find all files ending with .py
            for file_path in path_obj.glob("*.py"):
                if file_path.is_file():  # Ensure it's a file and not a directory
                    state_manager.connect_state_hook(STATES_DIR + file_path)
            # With this, you don't need to manually mention every state file in that directory.
            # Given that, that directory only contains state files to be loaded.

And adding the running mechanism, the final ``main.py`` file will look like-

.. admonition:: ``main.py`` file
    :class: seealso

    .. code-block:: python

        import pygame
        from game_state import StateManager
        from pathlib import Path

        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("Game State Hooks Example")


        def main() -> None:
            screen = pygame.display.set_mode((500, 600))
            # Create a basic 500x600 pixel window

            state_manager = StateManager(screen)
            STATES_DIR = "states."
            path_obj = Path(STATES_DIR)

            # Use glob to find all files ending with .py
            for file_path in path_obj.glob("*.py"):
                if file_path.is_file():  # Ensure it's a file and not a directory
                    state_manager.connect_state_hook(STATES_DIR + file_path)
            # With this, you don't need to manually mention every state file in that directory.
            # Given that, that directory only contains state files to be loaded.

            state_manager.change_state("MainMenu")
            # We need to use the name we supplied in the __init_sublcass__'s `state_name`.
            # If no state_name was passed, we use the class name itself.

            clock = pygame.time.Clock()

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

Now we need to make a few changes to our state files for it to accept hook
loading.

Let's first take a look at our ``states/games.py`` file. It initially looks
like this-

.. admonition:: ``states/games.py`` file
    :class: seealso

    .. code-block:: python

        import pygame
        from game_state import State

        BLUE = (0, 0, 255)


        class GameState(State, state_name="Game"):
            def __init__(self) -> None:
                self.player_x: float = 250.0
                self.speed = 200

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
                    self.player_x -= self.speed * dt

                if pressed[pygame.K_d]:
                    self.player_x += self.speed * dt

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

To add the state hook functionality, all we need to do is create a ``hook``
function in the file which loads the ``State`` to the ``StateManager``.
Like this-

.. admonition:: ``states/games.py`` file
    :class: seealso

    .. code-block:: python

        from typing import Any

        import pygame
        from game_state import State

        BLUE = (0, 0, 255)


        class GameState(State, state_name="Game"):
            def __init__(self) -> None:
                self.player_x: float = 250.0
                self.speed = 200

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
                    self.player_x -= self.speed * dt

                if pressed[pygame.K_d]:
                    self.player_x += self.speed * dt

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

        def hook(**kwargs: Any) -> None:
            # This function should be present below the State you want to load and should call
            # the `StateManager.load_states` method while passing in the State you want to laod
            GameState.manager.load_states(GameState, **kwargs)

Doing the same for ``states/main_menu.py``-

.. admonition:: ``states/games.py`` file
    :class: seealso

    .. code-block:: python

        from typing import Any

        import pygame
        from game_state import State

        GREEN = (0, 255, 0)


        class MainMenuState(State, state_name="MainMenu"):
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


        def hook(**kwargs: Any) -> None:
            # This function should be present below the State you want to load and should call
            # the `StateManager.load_states` method while passing in the State you want to laod
            MainMenuState.manager.load_states(MainMenuState, **kwargs)

That's all you need to do to use state hooks!

Running your ``main.py`` file will give you the same output as `Demo Output`_

All the code in this guide is available in the `examples <https://github.com/Jiggly-Balls/game-state/tree/main/examples>`_
directory of it's repository.