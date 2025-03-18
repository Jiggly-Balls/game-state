from __future__ import annotations

import pytest
from typing import Tuple, Type

from src.game_state import State, StateManager
from src.game_state.errors import ExitGame, ExitState


@pytest.fixture
def scenario() -> Tuple[StateManager, Type[State], Type[State]]:
    class StateOne(State, state_name="Test 1"): ...

    class StateTwo(State): ...

    return StateManager(...), StateOne, StateTwo


def test_load_states(
    scenario: Tuple[StateManager, State, State],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    manager.load_states(state_1, state_2)

    all_states = manager.get_state_map()
    assert (
        len(all_states) == 2
    ), "Loaded 2 states, did not receive 2 states back."
    assert (
        state_1.state_name in all_states
    ), f"Expected {state_1.state_name} in state map."
    assert (
        state_2.state_name in all_states
    ), f"Expected {state_2.state_name} in state map."


def test_change_states(
    scenario: Tuple[StateManager, Type[State], Type[State]],
) -> None:
    manager = scenario[0]
    state_1 = scenario[1]
    state_2 = scenario[2]

    manager.load_states(state_1, state_2)

    assert (
        manager.get_current_state() is None
    ), "Got a non-None value while no state was updated to."

    manager.change_state(state_1.state_name)

    assert (
        manager.get_current_state().state_name == state_1.state_name
    ), "Received wrong state instance upon changing."

    with pytest.raises(ExitState):
        manager.update_state()

    with pytest.raises(ExitGame):
        manager.exit_game()
