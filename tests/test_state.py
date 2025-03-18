from src.game_state import State


def test_state() -> None:
    state1_name = "First Screen"

    class ScreenOne(State, state_name=state1_name): ...

    class ScreenTwo(State): ...

    assert ScreenOne.state_name == state1_name
    assert ScreenTwo.state_name == "ScreenTwo"
