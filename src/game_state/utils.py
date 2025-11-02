from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Tuple


__all__ = ("MISSING",)


class StateArgs:
    def __init__(self, *, state_name: str, **kwargs: Any) -> None:
        self.state_name: str = state_name
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            + ", ".join(
                (
                    f"{key}={value}"
                    for key, value in zip(
                        self.__dict__.keys(), self.__dict__.values()
                    )
                )
            )
            + ")"
        )

    def __eq__(self, value: object) -> bool:
        return isinstance(value, StateArgs) and value.__dict__ == self.__dict__

    def __bool__(self) -> bool:
        # The StateArg having data other than `state_name` will be considered truthy.
        return len(self.__dict__) > 1


class _MissingSentinel:
    __slots__: Tuple[str, ...] = ()

    def __eq__(self, other: Any) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()
