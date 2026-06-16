from typing import Any

from src.game_state import State


class HookState1(State[Any]): ...  # noqa: D101


def hook() -> None:
    HookState1.manager.load_states(HookState1)
