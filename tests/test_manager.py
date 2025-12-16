from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import State, StateManager
from src.game_state.errors import StateError, StateLoadError

if TYPE_CHECKING:
    from typing import Any, Tuple, Type


@pytest.fixture
def scenario() -> Tuple[
    StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
]:
    class StateOne(State["Any"], state_name="Test 1"): ...

    class StateTwo(State["Any"]): ...

    manager = StateManager(...)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
    if TYPE_CHECKING:
        manager = StateManager[State["Any"]](...)  # pyright: ignore[reportArgumentType]

    return manager, StateOne, StateTwo


def test_load_states(
    scenario: Tuple[
        StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
    ],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    manager.load_states(state_1, state_2)

    with pytest.raises(StateLoadError):
        manager.load_states(state_1)

    assert len(manager.state_map) == 2, (
        "Loaded 2 states, did not receive 2 states back."
    )
    assert state_1.state_name in manager.state_map, (
        f"Expected {state_1.state_name} in state map."
    )
    assert state_2.state_name in manager.state_map, (
        f"Expected {state_2.state_name} in state map."
    )


def test_change_states(
    scenario: Tuple[
        StateManager[State["Any"]], Type[State["Any"]], Type[State["Any"]]
    ],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    manager.load_states(state_1, state_2)
    manager.change_state(state_1.state_name)

    assert manager.current_state is not None, (
        "Received NoneType for current state."
    )

    assert manager.current_state.state_name == state_1.state_name, (
        "Received wrong state instance upon changing."
    )

    with pytest.raises(StateError):
        manager.change_state("Invalid State Name")
