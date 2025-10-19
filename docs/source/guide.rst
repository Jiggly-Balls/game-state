Guide
=====

To get started with this library first create a new project and create a
virtual environment & activate it (optional but recommended). Once you've done
that you may continue.

Installation
------------

Install ``game_state`` through pip in your terminal-

.. code-block:: console

   (.venv) $ pip install game_state

Since ``game_state`` does not have any dependancies, we need to manually
install the pygame library (or ``pygame-ce`` if you're using that).

.. code-block:: console

   (.venv) $ pip install pygame-ce


Using the Library
-----------------

.. note::
   This library has been updated to version 2.0, introducing breaking changes that are not backward
   compatible with version 1.x.

   If you are using a version older than 2.0.0, refer to the v1 documentation for guidance:
   `game-state v1.1.3 Documentation <https://game-state.readthedocs.io/en/v1.1.3/guide.html#using-the-library>`_

   We highly recommend upgrading to version 2.0, as it offers significant optimizations and improvements over v1.

Let's create a simple pygame script having two screens. One screen will display
green colour and the other will display blue with a moveable red square.

.. admonition:: Setting up the basics
   :class: seealso

   .. code-block:: python

      import pygame

      from game_state import State, StateManager


      pygame.init()
      pygame.display.init()
      pygame.display.set_caption("Game State Example")

      speed = 100  # Player speed
      BLUE = (0, 255, 0)
      GREEN = (0, 0, 255)


Now that we have imported and set the display of our app, let's create a main
menu screen.

.. admonition:: Creating a simple screen
   :class: seealso

   .. code-block:: python

      class MainMenuState(State, state_name="MainMenu"):
         def process_event(self, event: pygame.event.Event) -> None:
            # This is executed in our our game loop for every event.

            if event.type == pygame.QUIT:
                  # We set the state manager's is_running variable to false
                  # which stops the game loop from continuing.
                  self.manager.is_running = False

         def process_update(self, dt: float) -> None:
            # This is executed in our game loop.

            self.window.fill(GREEN)
            pygame.display.update()


.. admonition:: Note
   :class: note

   In this library screens are referred to as ``State``\s and screen manager as
   ``StateManager``

Now that we have created a screen, let's add it to our screen manager and run it!

.. admonition:: Adding our screen to the state manager.
   :class: seealso

   .. code-block:: python

      def main() -> None:
         screen = pygame.display.set_mode((500, 700))
         # Create a basic 500x700 pixel window

         state_manager = StateManager(screen)
         state_manager.load_states(MainMenuState)
         # We pass in all the screens that we want to use in our game / app.

         state_manager.change_state("MainMenu") 
         # We need to use the name we supplied in the __init_sublcass__'s `state_name`.
         # If no state_name was passed, we use the class name itself.
         
         clock = pygame.time.Clock()

         while state_manager.is_running:
            # The state manager has a `is_running` attribute which is `True` by default

            dt = clock.tick(60) / 1000  # The delta time from the clock for frame rate independance.

            for event in pygame.event.get():
                  state_manager.current_state.process_event(event)
                  # Calling the event function of the running state.

            state_manager.current_state.process_update(dt)
            # Calling the update function of the running state.
         
      if __name__ == "__main__":
         main()

There you have it! We have set up a simple screen using the Game State library.
Adding more screens is just as simple as the subclassing ``State`` & adding it
to the ``StateManager``. 

.. admonition:: Adding the main game screen to our state manager.
    :class: seealso

    .. code-block:: python

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


        class GameState(State, state_name="Game"):
            def __init__(self) -> None:
                self.player_x: float = 250.0

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

Finally, we need to add our ``GameState`` to our ``StateManager`` just like
how we did for our ``MainMenuState``.

.. code-block:: python

    state_manager.load_states(MainMenuState, GameState)

There you go! We have made a simple pygame to handle multiple screens via Game
State! The final code will look something like this-

.. code-block:: python

    import pygame
    from game_state import State, StateManager

    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    speed = 200
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Game State Example")


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


    class GameState(State, state_name="Game"):
        def __init__(self) -> None:
            self.player_x: float = 250.0

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
        # Create a basic 500x600 pixel window

        state_manager = StateManager(screen)
        state_manager.load_states(MainMenuState, GameState)
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


Demo Output
-----------

Upon following this guide correctly, you will obtain an output similar to this-

.. image:: https://img.youtube.com/vi/QTN-YW8dv_I/maxresdefault.jpg
    :alt: Demo output video
    :target: https://www.youtube.com/watch?v=QTN-YW8dv_I

(Click to open the video)

.. :toctree::

   api