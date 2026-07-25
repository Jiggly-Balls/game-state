Overlay States
==============

From version ``2.5`` onwards the library supports **overlay states**. In this
guide we'll take a look at what overlay states are, how to open and close
them, and how they interact with the rest of the state manager.


What is an Overlay State?
--------------------------

So far, switching screens with ``StateManager.change_state`` fully replaces
whatever was previously running. This works well for full screen transitions
like ``MainMenu`` to ``Game``, but it falls apart for things like a pause
menu or a settings panel - screens that need to be drawn *on top of*
whatever is currently running, without losing that state's progress.

This is exactly what overlay states solve. Opening an overlay pushes a new
state on top of the currently running one without disturbing it. Closing the
overlay simply removes it, and whatever was running underneath picks back up
right where it left off.

A mock example to set the stage-

.. code-block:: python

  from game_state import State, StateManager


  class Game(State):
      def on_enter(self, previous_state) -> None:
          print("Entered Game.")


  class PauseMenu(State):
      def on_overlay_open(self, temporary: bool) -> None:
          print("Game paused.")

      def on_overlay_close(self, temporary: bool) -> None:
          print("Game resumed.")


  manager = StateManager(...)  # ... is a placeholder
  manager.load_states(Game, PauseMenu)
  manager.change_state("Game")

  overlay_id = manager.open_overlay("PauseMenu")
  # manager.current_state is now PauseMenu.

  manager.close_overlay(overlay_id)
  # manager.current_state is Game again, exactly as it was.

Running this gives us-

.. code-block::

  Entered Game.
  Game paused.
  Game resumed.

Notice that ``Game.on_enter`` is only called once. Opening and closing the
overlay never touches ``Game`` at all — it's simply hidden underneath while
the overlay is active.


Opening an Overlay
-------------------

Overlays are opened with ``StateManager.open_overlay``, passing in the
``state_name`` of the state you want to use as an overlay.

.. code-block:: python

  overlay_id = manager.open_overlay("PauseMenu")

This returns a ``state_id`` which you'll need later to close that specific
overlay. If you don't supply one yourself, the manager assigns an
incrementing integer automatically.

You can also assign your own ID-

.. code-block:: python

  manager.open_overlay("PauseMenu", "pause")

.. admonition:: Note
  :class: note

  It's recommended to use a string rather than an integer when assigning a
  custom ID. When no ID is supplied, the manager defaults to an incrementing
  integer counter for its overlay elements, which can conflict with custom
  integer IDs.

Only the newly opened overlay's ``State.on_overlay_open`` listener is called
when you open an overlay — no other global or state listeners run.


Closing an Overlay
--------------------

Overlays are closed with ``StateManager.close_overlay``, using the same
``state_id`` that was returned (or supplied) when it was opened.

.. code-block:: python

  manager.close_overlay("pause")

Unlike ``change_state``, you're not restricted to closing only the topmost
overlay, any opened overlay can be closed directly by its ID, regardless of
where it sits in the stack.

If you'd rather close everything at once, ``StateManager.close_all_overlays``
clears every opened overlay in one call, most recently opened first-

.. code-block:: python

  manager.close_all_overlays()

Just like opening, closing an overlay only calls that state's
``State.on_overlay_close`` listener. No other global or state listeners run.


Stacking Multiple Overlays
----------------------------

You're not limited to a single overlay at a time, nor to only one instance of
a given state. Opening the same state twice creates a fresh instance for the
second one rather than reusing the first-

.. code-block:: python

  first_id = manager.open_overlay("Notification", "toast-1")
  second_id = manager.open_overlay("Notification", "toast-2")
  # Two independent Notification instances are now stacked.

Each ``State`` instance carries a ``state_id`` attribute so it knows which
overlay slot it belongs to, and a ``temporary`` flag is passed to
``on_overlay_open`` / ``on_overlay_close`` to let you tell the first instance
of a state apart from any duplicates opened after it-

.. code-block:: python

  class Notification(State):
      def on_overlay_open(self, temporary: bool) -> None:
          if temporary:
              print("Another notification stacked on top.")
          else:
              print("First notification opened.")

.. admonition:: Note
  :class: note

  If the overlay you're opening was loaded with ``state_args``, any
  duplicate instances created for stacking reuse those same arguments
  automatically.


Overlays and ``change_state``
--------------------------------

By default, calling ``StateManager.change_state`` while an overlay is active
only swaps out the *base* state underneath — any open overlays are left
exactly as they are, and ``current_state`` will still point to the topmost
overlay.

.. code-block:: python

  manager.open_overlay("PauseMenu")
  manager.change_state("MainMenu")
  # current_state is still PauseMenu; MainMenu is now waiting underneath it.

If you'd rather clear every overlay as part of the transition, pass
``clear_overlays=True``-

.. code-block:: python

  manager.change_state("MainMenu", clear_overlays=True)
  # Every overlay is closed, and current_state is now MainMenu.


Putting It Together
----------------------

Here's a small pygame example that toggles a pause menu overlay with the
``Esc`` key, without losing any of the running game's state-

.. code-block:: python

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
              # Create a snapshot of the last frame and darken it.
              self.frame_snap = self.screen.copy()
              self.frame_snap.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)

      def on_overlay_close(self, temporary: bool) -> None:
          # This is called when either `StateManager.close_overlay` or `StateManager.close_all_overlays` fires.
          self.frame_snap = None

      def process_update(self, dt: float) -> None:
          # Draws a green "menu" box.
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

When you press `ESC` the game pauses and shows a green "menu" box.
Upon pressing `ESC` again, the game unpauses and resumes from where
you left off. This allows you to preserve the context of your original
state.

.. admonition:: Warning
  :class: warning

  Although it's possible to use ``open_overlay`` as a full replacement for
  ``change_state``, it's discouraged to do so if the overlays that are never
  cleared. This can cause memory leaks if used irresponsibly.
