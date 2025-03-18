![https://pypi.org/project/game-state/](https://img.shields.io/pypi/v/game-state.svg?style=for-the-badge&logo=pypi&color=blueviolet&logoColor=white)
![https://github.com/Jiggly-Balls/game-state/releases](https://img.shields.io/github/v/release/Jiggly-Balls/game-state?color=blueviolet&include_prereleases&label=Latest%20Release&logo=github&sort=semver&style=for-the-badge&logoColor=white)
![https://pypi.org/project/game-state/](https://img.shields.io/pypi/dm/game-state?color=blueviolet&logo=pypi&logoColor=white&style=for-the-badge)
![https://github.com/Jiggly-Balls/game-state/blob/main/LICENSE](https://img.shields.io/pypi/l/game-state?color=blueviolet&logo=c&logoColor=white&style=for-the-badge)
![https://game-state.readthedocs.io/en/latest/](https://img.shields.io/readthedocs/game-state?color=blueviolet&logo=readthedocs&logoColor=white&style=for-the-badge)
![](https://img.shields.io/pypi/pyversions/game-state.svg?color=blueviolet&style=for-the-badge&logo=python&logoColor=white)

# Game-State
A pygame utility package that allows you to handle different screens in an organized manner.

## Table of Contents

- [Analytics](#analytics)
- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Links](#links)

### Analytics
![Alt](https://repobeats.axiom.co/api/embed/cbb24e2ae82fdceeceba8291982821ddbc065897.svg "Repobeats analytics image")

### Requirements
This library supports python versions `3.8` - `3.13`.

### Installation
Create and activate a virtual environment in your workspace (optional) and run the following command-
```
pip install game_state
``` 
> **Note:** This package does not have any dependancy on `pygame`, hence you will need to install them separately on your own. This gives you the freedom to work with `pygame`, `pygame-ce` or any of it's forks.

### Getting Started
Let's create two simple screens and switch back and forth between them.

```py
import pygame

from game_state import State, StateManager
from game_state.errors import ExitGame, ExitState


pygame.init()
pygame.display.init()
pygame.display.set_caption("Game State Example")

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class FirstScreen(State):
   def run(self) -> None:
      while True:
            self.window.fill(GREEN)

            for event in pygame.event.get():
               if event.type == pygame.QUIT:
                  self.manager.exit_game()

               if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                  self.manager.change_state("SecondScreen")
                  self.manager.update_state()

            pygame.display.update()


class SecondScreen(State):
   def run(self) -> None:
      while True:
            self.window.fill(BLUE)

            for event in pygame.event.get():
               if event.type == pygame.QUIT:
                  self.manager.exit_game()

               if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                  self.manager.change_state(
                        "FirstScreen"
                  )
                  self.manager.update_state()

            pygame.display.update()


def main() -> None:
   screen = pygame.display.set_mode((500, 700))

   state_manager = StateManager(screen)
   state_manager.load_states(FirstScreen, SecondScreen)
   state_manager.change_state("FirstScreen")

   while True:
      try:
            state_manager.run_state()
      except ExitState as error:
            last_state = error.last_state
            current_state = state_manager.get_current_state()
            print(f"State has changed from: {last_state} to {current_state}")


if __name__ == "__main__":
   try:
      main()
   except ExitGame:
      print("Game has exited successfully")
```

You can have a look at the [game state guide](https://game-state.readthedocs.io/en/latest/guide.html#using-the-library) for a more detailed explaination.

### Links
- Guide & API Reference: https://game-state.readthedocs.io/en/stable/
- PyPI Page: https://pypi.org/project/game-state/