from src.game_state import State


class HookState1(State): ...


def hook() -> None:
    HookState1.manager.load_states(HookState1)
