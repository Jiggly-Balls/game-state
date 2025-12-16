from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from src.game_state import State

if TYPE_CHECKING:
    pass


class HookState1(State["Any"]):
    def on_load(self, reload: bool) -> None:
        print(self.manager.state_map)

    def on_enter(self, prevous_state: Optional[State["Any"]]) -> None:
        return super().on_enter(prevous_state)

    def on_leave(self, next_state: State["Any"]) -> None:
        print(next_state.manager.state_map)


def hook() -> None:
    HookState1.manager.load_states(HookState1)
