from typing import Any

from src.game_state import State


class HookState2(State[Any]): ...


def hook() -> None:
    HookState2.manager.load_states(HookState2)
