from __future__ import annotations

from typing import Tuple, Type

import pytest

from src.game_state import State, StateManager
from src.game_state.errors import StateError, StateLoadError


@pytest.fixture
def scenario() -> Tuple[StateManager, Type[State], Type[State]]:
    class StateOne(State, state_name="Test 1"): ...

    class StateTwo(State): ...

    manager = StateManager(...)  # pyright: ignore[reportArgumentType]

    return manager, StateOne, StateTwo


def test_load_states(
    scenario: Tuple[StateManager, Type[State], Type[State]],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    class NotAState: ...

    manager.load_states(state_1, state_2)

    with pytest.raises(StateLoadError):
        manager.load_states(state_1)

    with pytest.raises(StateError):
        manager.load_states(NotAState)  # pyright:ignore[reportArgumentType]

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
    scenario: Tuple[StateManager, Type[State], Type[State]],
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
