from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import AsyncState, AsyncStateManager
from src.game_state.errors import StateError, StateLoadError

if TYPE_CHECKING:
    from typing import Any, Tuple, Type


@pytest.fixture
def scenario() -> Tuple[
    AsyncStateManager[AsyncState["Any"]],
    Type[AsyncState["Any"]],
    Type[AsyncState["Any"]],
]:
    class StateOne(AsyncState["Any"], state_name="Test 1"): ...

    class StateTwo(AsyncState["Any"]): ...

    manager = AsyncStateManager[AsyncState["Any"]]()

    return manager, StateOne, StateTwo


@pytest.mark.asyncio
async def test_load_unload_states(
    scenario: Tuple[
        AsyncStateManager[AsyncState["Any"]],
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
    ],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    await manager.load_states(state_1, state_2)

    with pytest.raises(StateLoadError):
        await manager.load_states(state_1)

    assert len(manager.state_map) == 2, (
        "Loaded 2 states, did not receive 2 states back."
    )
    assert state_1.state_name in manager.state_map, (
        f"Expected {state_1.state_name} in state map."
    )
    assert state_2.state_name in manager.state_map, (
        f"Expected {state_2.state_name} in state map."
    )

    with pytest.raises(StateLoadError):
        await manager.unload_state("UNLOADED STATE")

    unloaded_state_1 = await manager.unload_state(state_1.state_name)
    assert unloaded_state_1 == state_1, (
        f"Expected state: {state_1=}, instead got {unloaded_state_1=}"
    )

    unloaded_state_2 = await manager.unload_state(state_2.state_name)
    assert unloaded_state_2 == state_2, (
        f"Expected state: {state_2=}, instead got {unloaded_state_2=}"
    )


@pytest.mark.asyncio
async def test_relaod_states() -> None:
    manager = AsyncStateManager[AsyncState["Any"]]()

    class BaseState(AsyncState["BaseState"]):
        reloaded: bool = False

    class StateOne(BaseState):
        async def on_load(self, reload: bool) -> None:
            BaseState.reloaded = reload

    await manager.load_states(StateOne)

    with pytest.raises(StateLoadError):
        await manager.reload_state("UNKOWN STATE")

    await manager.reload_state("StateOne")

    assert BaseState.reloaded, "Expected BaseState reload to be complete."


@pytest.mark.asyncio
async def test_change_states(
    scenario: Tuple[
        AsyncStateManager[AsyncState["Any"]],
        Type[AsyncState["Any"]],
        Type[AsyncState["Any"]],
    ],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    await manager.load_states(state_1, state_2)
    await manager.change_state(state_1.state_name)

    assert manager.current_state is not None, (
        "Received NoneType for current state."
    )

    assert manager.current_state.state_name == state_1.state_name, (
        "Received wrong state instance upon changing."
    )

    with pytest.raises(StateError):
        await manager.change_state("Invalid State Name")
