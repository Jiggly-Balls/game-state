from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import State, StateManager
from src.game_state.utils import StateArgs

if TYPE_CHECKING:
    from typing import Any, Tuple, Type


DATA_1: int = 1
DATA_2: str = "Guten Morgen"


@pytest.fixture
def manager() -> StateManager[State["Any"]]:
    manager = StateManager(...)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
    if TYPE_CHECKING:
        manager = StateManager[State["Any"]](...)  # pyright: ignore[reportArgumentType]

    return manager


@pytest.fixture
def states() -> Tuple[
    Type[State["Any"]],
    Type[State["Any"]],
    Type[State["Any"]],
]:
    class StateOne(State["Any"]):
        def __init__(self, data_1: int) -> None:
            assert data_1 == DATA_1, (
                f"Expected passed data to be {DATA_1}, instead got {data_1}."
            )

    class StateTwo(State["Any"]):
        def __init__(self, data_2: str) -> None:
            assert data_2 == DATA_2, (
                f"Expected passed data to be {DATA_2}, instead got {data_2}."
            )

    class StateThree(State["Any"]): ...

    return StateOne, StateTwo, StateThree


@pytest.fixture
def data() -> Tuple[StateArgs, StateArgs]:
    state_one_args = StateArgs(state_name="StateOne", data_1=DATA_1)
    state_two_args = StateArgs(state_name="StateTwo", data_2=DATA_2)

    return state_one_args, state_two_args


def test_state_args(
    manager: StateManager["State[Any]"],
    states: Tuple[
        Type[State["Any"]],
        Type[State["Any"]],
        Type[State["Any"]],
    ],
    data: Tuple[StateArgs, StateArgs],
) -> None:
    manager.load_states(
        *states,
        state_args=data,
    )


def test_lazy_state_args(
    manager: StateManager[State["Any"]],
    states: Tuple[
        Type[State["Any"]],
        Type[State["Any"]],
        Type[State["Any"]],
    ],
    data: Tuple[StateArgs, StateArgs],
) -> None:
    manager.add_lazy_states(*states, state_args=data)

    for state in states:
        # Initializes and passes data to the lazy states
        manager.change_state(state.state_name)


def test_remove_lazy_state_args(
    manager: StateManager[State["Any"]],
    states: Tuple[Type[State["Any"]], Type[State["Any"]], Type[State["Any"]]],
    data: Tuple[StateArgs, StateArgs],
) -> None:
    manager.add_lazy_states(*states, state_args=data)

    for state, resource in zip(states[:2], data):
        removed_resources = manager.remove_lazy_state(state.state_name)

        assert removed_resources is not None, (
            "Expected state class with state args, instead got `None`."
        )
        assert removed_resources[1] is not None, (
            "Expected state args, instead got `None`"
        )
        assert removed_resources[1][0] == resource, (
            f"Expected `{resource=}`. Instead got `{removed_resources[1][0]}`."
        )
