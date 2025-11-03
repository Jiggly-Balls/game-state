from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple


__all__ = ("StateArgs", "MISSING")


@dataclass()
class StateArgs:
    """A dataclass to send data to states while loading them in the manager.

    :param state_name:
        The name of the state which the argument belongs to.
    :param kwargs:
        The data that needs to be sent.
    """

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
        """Returns the data to be passed on to the state.
        The data returned does not contain ``state_name`` in it.

        :returns:
            The data of the state arg. Does not include ``state_name`` in it.
        """

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
"""Used in areas where an attribute doesn't have a value by default but
gets defined during runtime. Lesser type checking would be required by using
this, opposed to using some other default value such as ``None``."""
