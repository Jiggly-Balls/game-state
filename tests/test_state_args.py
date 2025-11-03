from __future__ import annotations

from src.game_state import State, StateManager
from src.game_state.utils import StateArgs


def test_state_args() -> None:
    DATA_1: int = 1
    DATA_2: str = "Guten Morgen"

    class StateOne(State):
        def __init__(self, data_1: int) -> None:
            assert data_1 == DATA_1, (
                f"Expected passed data to be {DATA_1}, instead got {data_1}."
            )

    class StateTwo(State):
        def __init__(self, data_2: str) -> None:
            assert data_2 == DATA_2, (
                f"Expected passed data to be {DATA_2}, instead got {data_2}."
            )

    class StateThree(State): ...

    state_one_args = StateArgs(state_name="StateOne", data_1=DATA_1)
    state_two_args = StateArgs(state_name="StateTwo", data_2=DATA_2)

    manager = StateManager(...)  # type: ignore
    manager.load_states(
        StateOne,
        StateTwo,
        StateThree,
        state_args=(state_one_args, state_two_args),
    )
