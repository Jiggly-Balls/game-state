from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Any

    from .manager import StateManager
    from .state import State

M = TypeVar("M", bound="StateManager[Any, Any]")
S = TypeVar("S", bound="State[Any, Any]")


class GenericRoot(Generic[M, S]): ...
