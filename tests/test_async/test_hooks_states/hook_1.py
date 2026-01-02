from typing import Any

from src.game_state import AsyncState


class HookState1(AsyncState[Any]): ...


async def hook() -> None:
    await HookState1.manager.load_states(HookState1)
