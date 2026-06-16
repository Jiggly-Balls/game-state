from typing import Any

from src.game_state import AsyncState


class HookState2(AsyncState[Any]): ...  # noqa: D101


async def hook() -> None:
    await HookState2.manager.load_states(HookState2)
