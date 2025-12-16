from typing import Any  # noqa: F401

from src.game_state import State


def test_state() -> None:
    state1_name = "First Screen"

    class ScreenOne(State["Any"], state_name=state1_name): ...

    class ScreenTwo(State["Any"]): ...

    assert ScreenOne.state_name == state1_name
    assert ScreenTwo.state_name == "ScreenTwo"
