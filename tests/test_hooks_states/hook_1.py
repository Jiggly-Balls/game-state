from __future__ import annotations

from typing import TYPE_CHECKING

from src.game_state import State

if TYPE_CHECKING:
    from typing import Any

    from src.game_state import StateManager


class HookState1(State[StateManager[Any]]): ...


def hook() -> None:
    HookState1.manager.load_states(HookState1)
