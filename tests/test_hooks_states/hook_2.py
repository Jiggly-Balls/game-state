from src.game_state import State


class HookState2(State): ...


def hook() -> None:
    HookState2.manager.load_states(HookState2)
