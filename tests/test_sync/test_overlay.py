from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import State, StateManager
from src.game_state.errors import OverlayError
from src.game_state.utils import StateArgs

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type


@pytest.fixture
def scenario() -> Tuple[
    StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
]:
    class BaseState(State["Any"], state_name="Base"): ...

    class OverlayState(State["Any"], state_name="Overlay"): ...

    manager = StateManager[State["Any"]]()
    manager.load_states(BaseState, OverlayState)
    manager.change_state("Base")

    return manager, BaseState, OverlayState


def test_open_overlay(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, overlay_state = scenario

    assert manager.current_state is not None, (
        "Expected a non-None current state before opening an overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the base state to be active before opening an overlay."
    )

    returned_id = manager.open_overlay("Overlay")

    assert isinstance(returned_id, int), (
        f"Expected an auto-generated integer ID, instead got `{returned_id!r}`."
    )
    assert manager.current_state is not None, (
        "Expected a non-None current state after opening an overlay."
    )
    assert manager.current_state.state_name == overlay_state.state_name, (
        "Expected the overlay state to be active after opening it."
    )


def test_open_overlay_with_custom_id(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager = scenario[0]
    CUSTOM_ID = "my-overlay"

    returned_id = manager.open_overlay("Overlay", CUSTOM_ID)

    assert returned_id == CUSTOM_ID, (
        f"Expected the custom ID `{CUSTOM_ID}` to be returned, "
        f"instead got `{returned_id!r}`."
    )


def test_open_overlay_duplicate_id_raises(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager = scenario[0]
    CUSTOM_ID = "duplicate-id"

    manager.open_overlay("Overlay", CUSTOM_ID)

    with pytest.raises(OverlayError):
        manager.open_overlay("Overlay", CUSTOM_ID)


def test_open_overlay_stacks_multiple_instances(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, _, overlay_state = scenario

    first_id = manager.open_overlay("Overlay")
    first_instance = manager.current_state

    second_id = manager.open_overlay("Overlay")
    second_instance = manager.current_state

    assert first_id != second_id, (
        "Expected two distinct auto-generated IDs for stacked overlays."
    )
    assert first_instance is not second_instance, (
        "Expected a fresh state instance to be created for the second "
        "overlay of the same state, instead the same instance was reused."
    )
    assert second_instance is not None, "Expected a non-None current state."
    assert second_instance.state_name == overlay_state.state_name, (
        "Expected the topmost overlay to share the same state name."
    )


def test_close_overlay(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, _ = scenario

    overlay_id = manager.open_overlay("Overlay")
    manager.close_overlay(overlay_id)

    assert manager.current_state is not None, (
        "Expected a non-None current state after closing the overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected to fall back to the base state after closing the "
        "only opened overlay."
    )


def test_close_overlay_unknown_id_raises(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager = scenario[0]

    with pytest.raises(OverlayError):
        manager.close_overlay("UNKNOWN ID")


def test_close_overlay_non_active(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager = scenario[0]

    bottom_id = manager.open_overlay("Overlay", "bottom")
    top_id = manager.open_overlay("Overlay", "top")

    top_instance = manager.current_state

    # Closing the non-active (bottom) overlay shouldn't disturb the
    # currently active (top) overlay.
    manager.close_overlay(bottom_id)

    assert manager.current_state is top_instance, (
        "Expected the active overlay to remain unchanged after closing "
        "a different, non-active overlay."
    )

    with pytest.raises(OverlayError):
        manager.close_overlay(bottom_id)

    manager.close_overlay(top_id)


def test_close_all_overlays(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, _ = scenario

    manager.open_overlay("Overlay", "one")
    manager.open_overlay("Overlay", "two")
    manager.open_overlay("Overlay", "three")

    manager.close_all_overlays()

    assert manager.current_state is not None, (
        "Expected a non-None current state after closing all overlays."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected to fall back to the base state after closing every "
        "opened overlay."
    )

    # Every previously used custom ID should now be reusable.
    manager.open_overlay("Overlay", "one")


def test_close_all_overlays_calls_in_reverse_order(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, _, _ = scenario
    close_order: List[Any] = []

    class TrackedOverlay(State["Any"], state_name="Tracked"):
        def on_overlay_close(self, temporary: bool) -> None:
            close_order.append(self.state_id)

    manager.load_states(TrackedOverlay)

    manager.open_overlay("Tracked", "first")
    manager.open_overlay("Tracked", "second")
    manager.open_overlay("Tracked", "third")

    manager.close_all_overlays()

    assert close_order == ["third", "second", "first"], (
        "Expected overlays to be closed from most recently opened to "
        f"first opened, instead got: {close_order}"
    )


def test_close_all_overlays_noop_with_no_overlays(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, _ = scenario

    # Should not raise or otherwise disturb the base state.
    manager.close_all_overlays()

    assert manager.current_state is not None, (
        "Expected a non-None current state."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the base state to remain active when there are no "
        "overlays to close."
    )


def test_overlay_hooks_are_called(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, _, _ = scenario
    opened_with: List[bool] = []
    closed_with: List[bool] = []

    class TrackedOverlay(State["Any"], state_name="Tracked"):
        def on_overlay_open(self, temporary: bool) -> None:
            opened_with.append(temporary)

        def on_overlay_close(self, temporary: bool) -> None:
            closed_with.append(temporary)

    manager.load_states(TrackedOverlay)

    overlay_id = manager.open_overlay("Tracked")
    assert opened_with == [False], (
        f"Expected `on_overlay_open` to be called once with `temporary=False` "
        f"for the first instance of a state, instead got: {opened_with}"
    )

    manager.close_overlay(overlay_id)
    assert closed_with == [False], (
        f"Expected `on_overlay_close` to be called once with `temporary=False`, "
        f"instead got: {closed_with}"
    )


def test_overlay_hooks_mark_duplicate_instances_temporary(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, _, _ = scenario
    opened_with: List[bool] = []

    class TrackedOverlay(State["Any"], state_name="Tracked"):
        def on_overlay_open(self, temporary: bool) -> None:
            opened_with.append(temporary)

    manager.load_states(TrackedOverlay)

    manager.open_overlay("Tracked")
    manager.open_overlay("Tracked")

    assert opened_with == [False, True], (
        "Expected the first instance to be marked non-temporary and every "
        f"instance after it to be marked temporary, instead got: {opened_with}"
    )


def test_open_overlay_with_state_args(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager = scenario[0]
    DATA = "some-payload"

    class DataOverlay(State["Any"], state_name="DataOverlay"):
        def __init__(self, data: str) -> None:
            assert data == DATA, (
                f"Expected passed data to be `{DATA}`, instead got `{data}`."
            )

    manager.load_states(
        DataOverlay,
        state_args=[StateArgs(state_name="DataOverlay", data=DATA)],
    )

    # Opening a duplicate overlay of the same state should reuse the
    # original state_args for the newly constructed, temporary instance.
    manager.open_overlay("DataOverlay")
    manager.open_overlay("DataOverlay")


def test_change_state_clears_overlays(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, _ = scenario

    manager.open_overlay("Overlay", "one")
    manager.open_overlay("Overlay", "two")

    manager.change_state(base_state.state_name, clear_overlays=True)

    assert manager.current_state is not None, (
        "Expected a non-None current state."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected only the base state to remain active after changing "
        "state with `clear_overlays=True`."
    )

    # IDs should be freed up again since the overlays were cleared.
    manager.open_overlay("Overlay", "one")


def test_change_state_keeps_overlays_by_default(
    scenario: Tuple[
        StateManager[State[Any]], Type[State[Any]], Type[State[Any]]
    ],
) -> None:
    manager, base_state, overlay_state = scenario

    overlay_id = manager.open_overlay("Overlay")
    overlay_instance = manager.current_state

    manager.change_state(base_state.state_name)

    assert manager.current_state is overlay_instance, (
        "Expected the active overlay to remain on top of the stack "
        "after `change_state` without `clear_overlays`."
    )
    assert manager.current_state is not None, (
        "Expected a non-None current state."
    )
    assert manager.current_state.state_name == overlay_state.state_name, (
        "Expected the overlay to still be reported as the current state."
    )

    manager.close_overlay(overlay_id)
    assert manager.current_state is not None, (
        "Expected a non-None current state after closing the overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the new base state to surface once the overlay was closed."
    )
