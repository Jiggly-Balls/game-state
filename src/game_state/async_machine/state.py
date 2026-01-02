from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar, overload

from ..utils import MISSING

if TYPE_CHECKING:
    from typing import Any, List, Literal, Optional, Type

    from .manager import AsyncStateManager


__all__ = ("AsyncState",)

S = TypeVar("S", bound="AsyncState[Any]")


class AsyncState(Generic[S], ABC):
    """The State class which works as an individual screen.

    :attributes:
        state_name: :class:`str`
            The name of the state. Has to be unique among other states.

            .. versionadded:: 1.1

        manager: :class:`AsyncStateManager`
            The manager to which the state is binded to.

            .. versionadded:: 1.0
    """

    state_name: str = MISSING
    manager: AsyncStateManager[AsyncState[S]] = MISSING

    _eager_states: List[Type[AsyncState[S]]] = []
    _lazy_states: List[Type[AsyncState[S]]] = []

    @overload
    def __init_subclass__(
        cls,
        *,
        state_name: Optional[str] = ...,
        eager_load: Literal[False] = ...,
        lazy_load: Literal[False] = ...,
    ) -> None: ...
    @overload
    def __init_subclass__(
        cls,
        *,
        state_name: Optional[str] = ...,
        eager_load: Literal[True] = ...,
        lazy_load: Literal[False] = ...,
    ) -> None: ...
    @overload
    def __init_subclass__(
        cls,
        *,
        state_name: Optional[str] = ...,
        eager_load: Literal[False] = ...,
        lazy_load: Literal[True] = ...,
    ) -> None: ...

    def __init_subclass__(
        cls,
        *,
        state_name: Optional[str] = None,
        eager_load: bool = False,
        lazy_load: bool = False,
    ) -> None:
        """Arguments you can pass while subclassing the State.

        :param state_name:
            | The name of the state. If no `state_name` is passed, it uses the identifier's name.

            .. versionadded:: 1.1

            .. code-block:: python

                class Game(AsyncState, state_name="GameState"): ...

        :param eager_load:
            | Automatically marks this class to be loaded eagerly.

            .. versionadded:: 2.2

            .. code-block:: python

                class MainMenu(AsyncState, eager_load=True): ...

        :param lazy_load:
            | Automatically marks this class to be loaded lazily.

            .. versionadded:: 2.2

            .. code-block:: python

                class PauseMenu(AsyncState, lazy_load=True): ...

        .. warning::

            You cannot set ``eager_load`` and ``lazy_load`` both to ``True``. You can only
            enable one (or none) of them.
        """

        cls.state_name = state_name or cls.__name__

        if lazy_load and eager_load:
            raise TypeError(
                "Cannot have both `lazy_load` and `eager_load` set to `True`."
                " The state must either load lazy or eager."
            )

        if eager_load:
            cls._eager_states.append(cls)

        elif lazy_load:
            cls._lazy_states.append(cls)

    async def on_load(self, reload: bool) -> None:
        r"""Called when the state is loaded into the :class:`AsyncStateManager`.

        This listener is invoked both during the initial load of the state and
        when the state is reloaded.

        .. versionadded:: 2.3.0

        .. warning::

            This method need not be called manually.

        :param reload:
            | A :class:`bool` indicating whether the state is being loaded for
              the first time (``False``) or reloaded (``True``).
        """
        pass

    async def on_unload(self, reload: bool) -> None:
        r"""Called when the state is being unloaded from the
        :class:`AsyncStateManager`.

        This listener is invoked both during the initial load of the state and
        when the state is reloaded.

        .. versionadded:: 2.3.0

        .. warning::

            This method need not be called manually.

        :param reload:
            | A :class:`bool` indicating whether the state is being unloaded for
              the first time (``False``) or reloaded (``True``).
        """
        pass

    async def on_enter(self, previous_state: Optional[S]) -> None:
        r"""This listener is called once when a state has been switched and is
        entering the current state.

        .. versionadded:: 2.0

        .. warning::

            This method need not be called manually.

        :param previous_state:
            | The state that was running previously. If there are no previous states,
              ``None`` is passed
        :type previous_state: typing.Optional[State]
        """
        pass

    async def on_leave(self, next_state: S) -> None:
        r"""This listener is called once when the state has been switched and is exiting
        the current one.

        .. versionadded:: 2.0

        .. warning::

            This method need not be called manually.

        :param next_state:
            | The next state that is going to be applied.
        :type next_state: State
        """
        pass
