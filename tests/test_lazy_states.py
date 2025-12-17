from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import State, StateManager
from src.game_state.errors import StateLoadError

if TYPE_CHECKING:
    from typing import Any, Tuple, Type


@pytest.fixture
def scenario() -> Tuple[
    StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
]:
    class StateOne(State["Any"]): ...

    class StateTwo(State["Any"]): ...

    manager = StateManager(...)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
    if TYPE_CHECKING:
        manager = StateManager[State["Any"]](...)  # pyright: ignore[reportArgumentType]

    return manager, StateOne, StateTwo


def test_lazy_states(
    scenario: Tuple[
        StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
    ],
) -> None:
    manager, eager_state, lazy_state = scenario

    manager.add_lazy_states(lazy_state)
    manager.load_states(eager_state)

    state_keys = manager.state_map.keys()

    assert lazy_state.state_name not in state_keys, (
        f"{lazy_state.state_name} was initialized eagerly."
    )
    assert eager_state.state_name in state_keys, (
        f"{eager_state.state_name} - eager state was not initialized."
    )

    manager.change_state(lazy_state.state_name)

    new_state_keys = manager.state_map.keys()

    for state in (eager_state, lazy_state):
        assert state.state_name in new_state_keys, (
            f"{state.state_name} was not initialized."
        )


def test_remove_lazy_states(
    scenario: Tuple[
        StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
    ],
) -> None:
    manager, EagerState, LazyState = scenario
    manager.add_lazy_states(LazyState)
    manager.load_states(EagerState)

    with pytest.raises(StateLoadError):
        manager.unload_state(LazyState.state_name)

    removed_resouce = manager.remove_lazy_state(EagerState.state_name)
    assert removed_resouce is None, (
        "Removing eager state from lazy state did not finish successfully. "
        f"Removed resources obtained: `{removed_resouce=}`. Expected `None`."
    )

    RemovedStateType = manager.unload_state(EagerState.state_name)
    assert RemovedStateType is EagerState, (
        "Unloaded state type was not the same as loaded state. "
        f"Expected: {EagerState}, instead got {RemovedStateType}."
    )

    removed_resouce = manager.remove_lazy_state(LazyState.state_name)
    assert removed_resouce is not None, (
        "Expected a tuple of lazy state with or without state args."
        " Instead got `None`"
    )
    assert removed_resouce[0] is LazyState, (
        "Removed state type was not the same as added state. "
        f"Expected: {LazyState}, instead got {removed_resouce[0]}."
    )
