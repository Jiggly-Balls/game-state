from __future__ import annotations

from typing import TYPE_CHECKING

from src.game_state import State

if TYPE_CHECKING:
    pass


class HookState1(State):
    def on_load(self, reload: bool) -> None:
        print(self.manager.state_map)  # <- Shows typing.Any


def hook() -> None:
    HookState1.manager.load_states(HookState1)
