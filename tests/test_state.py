from __future__ import annotations

from typing import TYPE_CHECKING

from src.game_state import State

if TYPE_CHECKING:
    from typing import Any


def test_state() -> None:
    state1_name = "First Screen"

    class ScreenOne(State[Any], state_name=state1_name): ...

    class ScreenTwo(State[Any]): ...

    assert ScreenOne.state_name == state1_name
    assert ScreenTwo.state_name == "ScreenTwo"
