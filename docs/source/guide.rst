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

Since ``game_state`` does not have any dependancies, we need to manually install
the pygame library (or ``pygame-ce`` if you're using that).

.. code-block:: console

   (.venv) $ pip install pygame


Using the Library
-----------------

Let's create a simple pygame script having two screens. One screen will display
blue colour and the other will display green.

.. admonition:: Setting up the basics
   :class: seealso

   .. code-block:: python

      import pygame

      from game_state import State, StateManager
      from game_state.errors import ExitGameError, ExitStateError

      pygame.init()
      pygame.display.init()
      pygame.display.set_caption("Game State Example")

      BLUE = (0, 255, 0)
      GREEN = (0, 0, 255)


Now that we have imported and set the display of our app, let's create it's screen.

.. admonition:: Creating a simple screen
   :class: seealso

   .. code-block:: python

      class FirstScreen(State):
         def run(self) -> None:
            # The run function executes as soon as the state has been changed to it.

            while True:
                  # Our game-loop

                  self.window.fill(GREEN)

                  for event in pygame.event.get():
                     if event.type == pygame.QUIT:
                        # Upon quitting, we raise the ExitGameError which we handle outside.
                        
                        raise ExitGameError()

                  pygame.display.update()  # Refreshes the screen

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
         state_manager.load_states(FirstScreen)
         # We pass in all the screens that we want to use in our game / app.
         
         state_manager.change_state("FirstScreen")
         # Updates the current state to the desired state (screen) we want.

         while True:
            try:
                  state_manager.run_state()
                  # This is the entry point of our screen manager.
                  # This should only be called once at start up.

            except ExitStateError as error:
                  # Stuff you can do right after a state (screen) has been changed
                  # i.e. Save player data, pause / resume / change music, etc...

                  last_state = error.last_state
                  current_state = state_manager.get_current_state()
                  print(f"State has changed from: {last_state} to {current_state}")

      if __name__ == "__main__":
         try:
            main()
         except ExitGameError:
            print("Game has exited successfully")

.. admonition:: Note
   :class: note

   Note that we can also handle the ``ExitGameError`` inside the ``main`` function
   instead. But we'd have to break out of the loop manually too.

There you have it! We have set up a simple game using the Game State library.
But now what if you want to create multiple screens and switch back and forth
between them? Worry not! It's as simple as creating another subclass of the
``State`` class & adding it to the ``StateManager``. 


.. admonition:: Adding another screen to our state manager.
   :class: seealso

   .. code-block:: python

      class FirstScreen(State):
         def run(self) -> None:
            # The run function executes as soon as the state has been changed to it.

            while True:
                  # Game loop of the first screen

                  self.window.fill(GREEN)

                  for event in pygame.event.get():
                     if event.type == pygame.QUIT:
                        # Upon quitting, we raise the ExitGameError which we handle outside.
                        
                        raise ExitGameError()

                     if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                        # Check if we're clicking the " c " button.
                        # If the condition is met, we change our screen to "SecondScreen" and update
                        # the state in the manager. 

                        self.manager.change_state("SecondScreen")
                        self.manager.update_state()

                  pygame.display.update()  # Refreshes the screen


      class SecondScreen(State):
         def run(self) -> None:
            # The exact same thing happens in the SecondScreen except we use a different
            # colour for the screen & we change our current state to FirstScreen if the
            # user presses " c ".

            while True:
               # Game loop of the second screen

                  self.window.fill(BLUE)

                  for event in pygame.event.get():
                     if event.type == pygame.QUIT:
                        raise ExitGameError()

                     if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                        self.manager.change_state("FirstScreen")  # Change our state to FirstScreen.
                        self.manager.update_state()  # Updates / resets the state.

                  pygame.display.update()

Finally, we need to add our ``SecondScreen`` to our ``StateManager`` just like
how we did for our ``FirstScreen``.

.. code-block:: python

   state_manager.load_states(FirstScreen, SecondScreen)

There you go! We have made a simple pygame to handle multiple screens via Game
State! The final code will looks something like this-

.. code-block:: python

   import pygame

   from game_state import State, StateManager
   from game_state.errors import ExitGameError, ExitStateError

   pygame.init()
   pygame.display.init()
   pygame.display.set_caption("Game State Example")


   GREEN = (0, 255, 0)
   BLUE = (0, 0, 255)


   class FirstScreen(State):
      def run(self) -> None:
         # The run function executes as soon as the state has been changed to it.

         while True:
               # Our game-loop

               self.window.fill(GREEN)

               for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                     # Upon quitting, we raise the ExitGameError which we handle outside.

                     raise ExitGameError()

                  if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                     # Check if we're clicking the " c " button.
                     # If the condition is met, we change our screen to "SecondScreen" and update
                     # the state in the manager.

                     self.manager.change_state("SecondScreen")
                     self.manager.update_state()

               pygame.display.update()  # Refreshes the screen


   class SecondScreen(State):
      def run(self) -> None:
         # The exact same thing happens in the SecondScreen except we use a different
         # colour for the screen & we change our current state to FirstScreen if the
         # user presses " c ".

         while True:
               self.window.fill(BLUE)

               for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                     raise ExitGameError()

                  if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                     self.manager.change_state(
                           "FirstScreen"
                     )  # Change our state to FirstScreen.
                     self.manager.update_state()  # Updates / resets the state.

               pygame.display.update()


   def main() -> None:
      screen = pygame.display.set_mode((500, 700))
      # Create a basic 500x700 pixel window

      state_manager = StateManager(screen)
      state_manager.load_states(FirstScreen, SecondScreen)
      # We pass in all the screens that we want to use in our game / app.

      state_manager.change_state("FirstScreen")
      # Updates the current state to the desired state (screen) we want.

      while True:
         try:
               state_manager.run_state()
               # This is the entry point of our screen manager.
               # This should only be called once at start up.

         except ExitStateError as error:
               # Stuff you can do right after a state (screen) has been changed
               # i.e. Save player data, pause / resume / change music, etc...

               last_state = error.last_state
               current_state = state_manager.get_current_state()
               print(f"State has changed from: {last_state} to {current_state}")


   if __name__ == "__main__":
      try:
         main()
      except ExitGameError:
         print("Game has exited successfully")



.. :toctree::

   guide
   api