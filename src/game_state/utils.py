from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple


__all__ = ("StateArgs", "MISSING")


@dataclass()
class StateArgs:
    state_name: str

    def __init__(self, *, state_name: str, **kwargs: Any) -> None:
        self.state_name = state_name
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

    def get_data(self) -> Dict[str, Any]:
        attributes = self.__dict__.copy()
        del attributes["state_name"]
        return attributes


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
