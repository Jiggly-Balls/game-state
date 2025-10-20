from src.game_state import StateManager


def test_hooks() -> None:
    state_manager = StateManager(...)  # pyright: ignore[reportArgumentType]

    state_manager.connect_state_hook("tests.test_hooks_states.hook_1")
    state_manager.connect_state_hook("tests.test_hooks_states.hook_2")

    state_1_name = "HookState1"

    state_manager.change_state(state_1_name)

    assert state_manager.current_state is not None, "Expected non-None value."

    assert state_manager.current_state.state_name == state_1_name, (
        f"Expected `{state_1_name}` as current state, instead got {state_manager.current_state}"
    )
