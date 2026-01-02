from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import AsyncState, AsyncStateManager
from src.game_state.utils import StateArgs

if TYPE_CHECKING:
    from typing import Any, Tuple, Type


DATA_1: int = 1
DATA_2: str = "Guten Morgen"


@pytest.fixture
def manager() -> AsyncStateManager[AsyncState["Any"]]:
    manager = AsyncStateManager[AsyncState["Any"]]()

    return manager


@pytest.fixture
def states() -> Tuple[
    Type[AsyncState["Any"]],
    Type[AsyncState["Any"]],
    Type[AsyncState["Any"]],
]:
    class StateOne(AsyncState["Any"]):
        def __init__(self, data_1: int) -> None:
            assert data_1 == DATA_1, (
                f"Expected passed data to be {DATA_1}, instead got {data_1}."
            )

    class StateTwo(AsyncState["Any"]):
        def __init__(self, data_2: str) -> None:
            assert data_2 == DATA_2, (
                f"Expected passed data to be {DATA_2}, instead got {data_2}."
            )

    class StateThree(AsyncState["Any"]): ...

    return StateOne, StateTwo, StateThree


@pytest.fixture
def data() -> Tuple[StateArgs, StateArgs]:
    state_one_args = StateArgs(state_name="StateOne", data_1=DATA_1)
    state_two_args = StateArgs(state_name="StateTwo", data_2=DATA_2)

    return state_one_args, state_two_args


@pytest.mark.asyncio
async def test_state_args(
    manager: AsyncStateManager["AsyncState[Any]"],
    states: Tuple[
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
    ],
    data: Tuple[StateArgs, StateArgs],
) -> None:
    await manager.load_states(
        *states,
        state_args=data,
    )


@pytest.mark.asyncio
async def test_lazy_state_args(
    manager: AsyncStateManager[AsyncState["Any"]],
    states: Tuple[
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
    ],
    data: Tuple[StateArgs, StateArgs],
) -> None:
    manager.add_lazy_states(*states, state_args=data)

    for state in states:
        # Initializes and passes data to the lazy states
        await manager.change_state(state.state_name)


@pytest.mark.asyncio
async def test_remove_lazy_state_args(
    manager: AsyncStateManager[AsyncState["Any"]],
    states: Tuple[
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
    ],
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
