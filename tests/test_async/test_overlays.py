from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.game_state import AsyncState, AsyncStateManager
from src.game_state.errors import OverlayError
from src.game_state.utils import StateArgs

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type


@pytest.fixture
def scenario() -> Tuple[
    AsyncStateManager[AsyncState[Any]],
    Type[AsyncState[Any]],
    Type[AsyncState[Any]],
]:
    class BaseState(AsyncState["Any"], state_name="Base"): ...

    class OverlayState(AsyncState["Any"], state_name="Overlay"): ...

    manager = AsyncStateManager[AsyncState["Any"]]()

    return manager, BaseState, OverlayState


@pytest.mark.asyncio
async def test_open_overlay(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    assert manager.current_state is not None, (
        "Expected a non-None current state before opening an overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the base state to be active before opening an overlay."
    )

    returned_id = await manager.open_overlay(overlay_state.state_name)

    assert isinstance(returned_id, int), (
        f"Expected an auto-generated integer ID, instead got `{returned_id!r}`."
    )
    assert manager.current_state is not None, (
        "Expected a non-None current state after opening an overlay."
    )
    assert manager.current_state.state_name == overlay_state.state_name, (
        "Expected the overlay state to be active after opening it."
    )


@pytest.mark.asyncio
async def test_open_overlay_with_custom_id(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    CUSTOM_ID = "my-overlay"
    returned_id = await manager.open_overlay(
        overlay_state.state_name, CUSTOM_ID
    )

    assert returned_id == CUSTOM_ID, (
        f"Expected the custom ID `{CUSTOM_ID}` to be returned, "
        f"instead got `{returned_id!r}`."
    )


@pytest.mark.asyncio
async def test_open_overlay_duplicate_id_raises(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    CUSTOM_ID = "duplicate-id"
    await manager.open_overlay(overlay_state.state_name, CUSTOM_ID)

    with pytest.raises(OverlayError):
        await manager.open_overlay(overlay_state.state_name, CUSTOM_ID)


@pytest.mark.asyncio
async def test_open_overlay_stacks_multiple_instances(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    first_id = await manager.open_overlay(overlay_state.state_name)
    first_instance = manager.current_state

    second_id = await manager.open_overlay(overlay_state.state_name)
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


@pytest.mark.asyncio
async def test_close_overlay(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    overlay_id = await manager.open_overlay(overlay_state.state_name)
    await manager.close_overlay(overlay_id)

    assert manager.current_state is not None, (
        "Expected a non-None current state after closing the overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected to fall back to the base state after closing the "
        "only opened overlay."
    )


@pytest.mark.asyncio
async def test_close_overlay_unknown_id_raises(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    with pytest.raises(OverlayError):
        await manager.close_overlay("UNKNOWN ID")


@pytest.mark.asyncio
async def test_close_overlay_non_active(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    bottom_id = await manager.open_overlay(overlay_state.state_name, "bottom")
    top_id = await manager.open_overlay(overlay_state.state_name, "top")

    top_instance = manager.current_state

    # Closing the non-active (bottom) overlay shouldn't disturb the
    # currently active (top) overlay.
    await manager.close_overlay(bottom_id)

    assert manager.current_state is top_instance, (
        "Expected the active overlay to remain unchanged after closing "
        "a different, non-active overlay."
    )

    with pytest.raises(OverlayError):
        await manager.close_overlay(bottom_id)

    await manager.close_overlay(top_id)


@pytest.mark.asyncio
async def test_close_all_overlays(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    await manager.open_overlay(overlay_state.state_name, "one")
    await manager.open_overlay(overlay_state.state_name, "two")
    await manager.open_overlay(overlay_state.state_name, "three")

    await manager.close_all_overlays()

    assert manager.current_state is not None, (
        "Expected a non-None current state after closing all overlays."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected to fall back to the base state after closing every "
        "opened overlay."
    )

    # Every previously used custom ID should now be reusable.
    await manager.open_overlay(overlay_state.state_name, "one")


@pytest.mark.asyncio
async def test_close_all_overlays_calls_in_reverse_order(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, _ = scenario
    close_order: List[Any] = []

    class TrackedOverlay(AsyncState["Any"], state_name="Tracked"):
        async def on_overlay_close(self, temporary: bool) -> None:
            close_order.append(self.state_id)

    await manager.load_states(base_state, TrackedOverlay)
    await manager.change_state(base_state.state_name)

    await manager.open_overlay(TrackedOverlay.state_name, "first")
    await manager.open_overlay(TrackedOverlay.state_name, "second")
    await manager.open_overlay(TrackedOverlay.state_name, "third")

    await manager.close_all_overlays()

    assert close_order == ["third", "second", "first"], (
        "Expected overlays to be closed from most recently opened to "
        f"first opened, instead got: {close_order}"
    )


@pytest.mark.asyncio
async def test_close_all_overlays_noop_with_no_overlays(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    # Should not raise or otherwise disturb the base state.
    await manager.close_all_overlays()

    assert manager.current_state is not None, (
        "Expected a non-None current state."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the base state to remain active when there are no "
        "overlays to close."
    )


@pytest.mark.asyncio
async def test_overlay_hooks_are_called(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, _ = scenario
    opened_with: List[bool] = []
    closed_with: List[bool] = []

    class TrackedOverlay(AsyncState["Any"], state_name="Tracked"):
        async def on_overlay_open(self, temporary: bool) -> None:
            opened_with.append(temporary)

        async def on_overlay_close(self, temporary: bool) -> None:
            closed_with.append(temporary)

    await manager.load_states(base_state, TrackedOverlay)
    await manager.change_state(base_state.state_name)

    overlay_id = await manager.open_overlay(TrackedOverlay.state_name)
    assert opened_with == [False], (
        f"Expected `on_overlay_open` to be called once with `temporary=False` "
        f"for the first instance of a state, instead got: {opened_with}"
    )

    await manager.close_overlay(overlay_id)
    assert closed_with == [False], (
        f"Expected `on_overlay_close` to be called once with `temporary=False`, "
        f"instead got: {closed_with}"
    )


@pytest.mark.asyncio
async def test_overlay_hooks_mark_duplicate_instances_temporary(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, _ = scenario
    opened_with: List[bool] = []

    class TrackedOverlay(AsyncState["Any"], state_name="Tracked"):
        async def on_overlay_open(self, temporary: bool) -> None:
            opened_with.append(temporary)

    await manager.load_states(base_state, TrackedOverlay)
    await manager.change_state(base_state.state_name)

    await manager.open_overlay(TrackedOverlay.state_name)
    await manager.open_overlay(TrackedOverlay.state_name)

    assert opened_with == [False, True], (
        "Expected the first instance to be marked non-temporary and every "
        f"instance after it to be marked temporary, instead got: {opened_with}"
    )


@pytest.mark.asyncio
async def test_open_overlay_with_state_args(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, _ = scenario
    await manager.load_states(base_state)
    await manager.change_state(base_state.state_name)

    DATA = "some-payload"

    class DataOverlay(AsyncState["Any"], state_name="DataOverlay"):
        def __init__(self, data: str) -> None:
            assert data == DATA, (
                f"Expected passed data to be `{DATA}`, instead got `{data}`."
            )

    await manager.load_states(
        DataOverlay,
        state_args=[StateArgs(state_name="DataOverlay", data=DATA)],
    )

    # Opening a duplicate overlay of the same state should reuse the
    # original state_args for the newly constructed, temporary instance.
    await manager.open_overlay(DataOverlay.state_name)
    await manager.open_overlay(DataOverlay.state_name)


@pytest.mark.asyncio
async def test_change_state_clears_overlays(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    await manager.open_overlay(overlay_state.state_name, "one")
    await manager.open_overlay(overlay_state.state_name, "two")

    await manager.change_state(base_state.state_name, clear_overlays=True)

    assert manager.current_state is not None, (
        "Expected a non-None current state."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected only the base state to remain active after changing "
        "state with `clear_overlays=True`."
    )

    # IDs should be freed up again since the overlays were cleared.
    await manager.open_overlay(overlay_state.state_name, "one")


@pytest.mark.asyncio
async def test_change_state_keeps_overlays_by_default(
    scenario: Tuple[
        AsyncStateManager[AsyncState[Any]],
        Type[AsyncState[Any]],
        Type[AsyncState[Any]],
    ],
) -> None:
    manager, base_state, overlay_state = scenario
    await manager.load_states(base_state, overlay_state)
    await manager.change_state(base_state.state_name)

    overlay_id = await manager.open_overlay(overlay_state.state_name)
    overlay_instance = manager.current_state

    await manager.change_state(base_state.state_name)

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

    await manager.close_overlay(overlay_id)
    assert manager.current_state is not None, (
        "Expected a non-None current state after closing the overlay."
    )
    assert manager.current_state.state_name == base_state.state_name, (
        "Expected the new base state to surface once the overlay was closed."
    )
