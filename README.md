<div align="center">

[![PyPI](https://img.shields.io/pypi/v/game-state.svg?style=for-the-badge&logo=pypi&color=blueviolet&logoColor=white)](https://pypi.org/project/game-state/)
[![Github Releases](https://img.shields.io/github/v/release/Jiggly-Balls/game-state?color=blueviolet&include_prereleases&label=Latest%20Release&logo=github&sort=semver&style=for-the-badge&logoColor=white)](https://github.com/Jiggly-Balls/game-state/releases)
[![Downloads](https://img.shields.io/pypi/dm/game-state?label=Downloads%20/%20Month&color=blueviolet&logo=pypi&logoColor=white&style=for-the-badge)](https://pypi.org/project/game-state/)
[![PyPI Downloads](https://img.shields.io/pepy/dt/game-state?label=Total%20Downloads&color=blueviolet&logo=pypi&logoColor=white&style=for-the-badge)](https://pepy.tech/projects/game-state)
[![License](https://img.shields.io/pypi/l/game-state?color=blueviolet&logo=c&logoColor=white&style=for-the-badge)](https://github.com/Jiggly-Balls/game-state/blob/main/LICENSE)
[![Docs](https://img.shields.io/readthedocs/game-state?color=blueviolet&logo=readthedocs&logoColor=white&style=for-the-badge)](https://game-state.readthedocs.io/en/latest/)
![Versions](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?color=blueviolet&logo=python&logoColor=white&style=for-the-badge)

</div>

# Game-State

A pygame utility package that allows you to handle different screens in an organized manner.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Links](#links)

### Requirements

This library supports python versions `3.8` - `3.14`.

### Installation

Create and activate a virtual environment in your workspace (optional) and run the following command-

```
pip install game_state
```

> **Note:** This package does not have any dependancy on `pygame`, hence you will need to install them separately on your own. This gives you the freedom to work with `pygame`, `pygame-ce` or any of it's forks.

### Getting Started

This is an example of creating two screens.
One displaying green colour and the other blue with a player.

```py
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
      if event.type == pygame.QUIT:
            self.manager.is_running = False

      if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            self.manager.change_state("Game")

   def process_update(self, dt: float) -> None:
      self.window.fill(GREEN)
      pygame.display.update()


class GameState(State, state_name="Game"):
   def __init__(self) -> None:
      self.player_x = 250

   def process_event(self, event: pygame.event.Event) -> None:
      if event.type == pygame.QUIT:
            self.manager.is_running = False

      if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            self.manager.change_state("MainMenu")

   def process_update(self, dt: float) -> None:
      self.window.fill(BLUE)
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

   state_manager = StateManager(screen)
   state_manager.load_states(MainMenuState, GameState)
   state_manager.change_state("MainMenu")

   clock = pygame.time.Clock()

   while state_manager.is_running:
      dt = clock.tick(60) / 1000

      for event in pygame.event.get():
            state_manager.current_state.process_event(event)

      state_manager.current_state.process_update(dt)

if __name__ == "__main__":
   main()
```

You can have a look at the [game state guide](https://game-state.readthedocs.io/en/latest/guide.html#using-the-library) for a more detailed explaination.

### Links

- Guide & API Reference: https://game-state.readthedocs.io/en/stable/
- PyPI Page: https://pypi.org/project/game-state/
