import pytest

from src.game_state import StateManager
from src.game_state.errors import StateError


def test_hooks() -> None:
    state_manager = StateManager(...)  # pyright: ignore[reportArgumentType]

    state_manager.connect_state_hook("tests.test_hooks_states.hook_1")
    state_manager.connect_state_hook("tests.test_hooks_states.hook_2")

    STATE_1_NAME = "HookState1"
    TOTAL_VALID_LOADED_STATES: int = 2

    state_manager.change_state(STATE_1_NAME)

    assert state_manager.current_state is not None, "Expected non-None value."

    assert state_manager.current_state.state_name == STATE_1_NAME, (
        f"Expected `{STATE_1_NAME}` as current state, instead got {state_manager.current_state}"
    )

    with pytest.raises(StateError):
        state_manager.connect_state_hook("tests.test_hooks_states.hook_3")

    loaded_states = len(state_manager.state_map)

    assert loaded_states == TOTAL_VALID_LOADED_STATES, (
        f"Expected {TOTAL_VALID_LOADED_STATES} loaded states, insted got {loaded_states}"
    )
