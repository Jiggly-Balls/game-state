from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from .errors import StateError, StateLoadError
from .state import State

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Dict, NoReturn, Optional, Type

    from pygame import Surface


class StateManager:
    """The State Manager used for managing multiple State(s).

    :param window:
        The main game window.
    """

    __slots__ = (
        "is_running",
        "_global_on_setup",
        "_global_on_enter",
        "_global_on_leave",
        "_states",
        "_current_state",
        "_last_state",
    )

    def __init__(self, window: Surface) -> None:
        State.window = window
        State.manager = self

        self.is_running = True

        self._global_on_setup: Optional[Callable[[State], None]] = None
        self._global_on_enter: Optional[
            Callable[[State, Optional[State]], None]
        ] = None
        self._global_on_leave: Optional[
            Callable[[Optional[State], State], None]
        ] = None

        self._states: Dict[str, State] = {}
        self._current_state: Optional[State] = None
        self._last_state: Optional[State] = None

    @property
    def current_state(self) -> Optional[State]:
        """The current state if applied. Will be ``None`` otherwise."""
        return self._current_state

    @current_state.setter
    def current_state(self, _: Any) -> NoReturn:
        raise ValueError(
            "Cannot overwrite the current state. Use `StateManager.change_state` instead."
        )

    @property
    def global_on_enter(
        self,
    ) -> Optional[Callable[[State, Optional[State]], None]]:
        return self._global_on_enter

    @global_on_enter.setter
    def global_on_enter(
        self, value: Callable[[State, Optional[State]], None]
    ) -> None:
        self._global_on_enter = value

    @property
    def global_on_leave(
        self,
    ) -> Optional[Callable[[Optional[State], State], None]]:
        return self._global_on_leave

    @global_on_leave.setter
    def global_on_leave(
        self, value: Callable[[Optional[State], State], None]
    ) -> None:
        self._global_on_leave = value

    @property
    def global_on_setup(self) -> Optional[Callable[[State], None]]:
        """The global ``on_setup`` function for all states.

        .. note::
            This has to be assigned before loading the states into the manager.
        """
        return self._global_on_setup

    @global_on_setup.setter
    def global_on_setup(self, value: Callable[[State], None]) -> None:
        self._global_on_setup = value

    @property
    def last_state(self) -> Optional[State]:
        """The last state object if any. Will be ``None`` otherwise"""
        return self._last_state

    @last_state.setter
    def last_state(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the last state.")

    @property
    def state_map(self) -> Dict[str, State]:
        """A dictionary copy of all the state names mapped to their respective instance."""
        return self._states.copy()

    @state_map.setter
    def state_map(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the state map.")

    def change_state(self, state_name: str) -> None:
        """Changes the current state and updates the last state.

        :param state_name:
            | The name of the State you want to switch to.

        :raises:
            :exc:`StateError`
                | Raised when the state name doesn't exist in the manager.
        """

        if state_name not in self._states:
            raise StateError(
                f"State `{state_name}` isn't present from the available states: "
                f"`{', '.join(self.get_state_map().keys())}`.",
                last_state=self._last_state,
            )

        self._last_state = self._current_state
        self._current_state = self._states[state_name]
        if self._global_on_leave:
            self._global_on_leave(self._last_state, self._current_state)

        if self._last_state:
            self._last_state.on_leave(self._current_state)

        if self._global_on_enter:
            self._global_on_enter(self._current_state, self._last_state)
        self._current_state.on_enter(self._last_state)

    def connect_state_hook(self, path: str, **kwargs: Any) -> None:
        r"""Calls the hook function of the state file.

        :param path:
            | The path to the State file containing the hook function to be called.
        :param \**kwargs:
            | The keyword arguments to be passed to the hook function.

        :raises:
            :exc:`StateError`
                | Raised when the hook function was not found in the state file to be loaded.
        """

        state = importlib.import_module(path)
        if "hook" not in state.__dict__:
            raise StateError(
                "\nAn error occurred in loading State Path-\n"
                f"`{path}`\n"
                "`hook` function was not found in state file to load.\n",
                last_state=self._last_state,
                **kwargs,
            )

        state.__dict__["hook"](**kwargs)

    def load_states(
        self, *states: Type[State], force: bool = False, **kwargs: Any
    ) -> None:
        r"""Loads the States into the StateManager.

        :param states:
            | The States to be loaded into the manager.

        :param force:
            | Default ``False``.
            |
            | Loads the State regardless of whether the State has already been loaded or not
            | without raising any internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed to the State's subclass on instantiation.

        :raises:
            :exc:`StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.
        """

        for state in states:
            if not force and state.state_name in self._states:
                raise StateLoadError(
                    f"State: {state.state_name} has already been loaded.",
                    last_state=self._last_state,
                    **kwargs,
                )

            self._states[state.state_name] = state(**kwargs)
            if self._global_on_setup:
                self._global_on_setup(self._states[state.state_name])
            self._states[state.state_name].on_setup()

    def reload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> State:
        r"""Reloads the specified State. A short hand to ``StateManager.unload_state`` &
        ``StateManager.load_state``.

        :param state_name:
            | The ``State`` name to be reloaded.

        :param force:
            | Default ``False``.
            |
            | Reloads the State even if it's an actively running State without
            | raising any internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed to the
            | ``StateManager.unload_state`` & ``StateManager.load_state``.

        :returns:
            | Returns the newly made :class:`State` instance.

        :raises:
            :exc:`StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.
        """

        deleted_cls = self.unload_state(
            state_name=state_name, force=force, **kwargs
        )
        self.load_states(deleted_cls, force=force, **kwargs)
        return self._states[state_name]

    def unload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> Type[State]:
        r"""Unloads the ``State`` from the ``StateManager``.

        :param state_name:
            | The State to be loaded into the manager.

        :param force:
            | Default ``False``.
            |
            | Unloads the State even if it's an actively running State without raising any
            | internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :returns:
            | The :class:`State` class of the deleted State name.

        :raises:
            :exc:`StateLoadError`
                | Raised when the state doesn't exist in the manager to be unloaded.

            :exc:`StateError`
                | Raised when trying to unload an actively running State.
                | Only raised when ``force`` is set to ``False``.
        """

        if state_name not in self._states:
            raise StateLoadError(
                f"State: {state_name} doesn't exist to be unloaded.",
                last_state=self._last_state,
                **kwargs,
            )

        elif (
            not force
            and self._current_state is not None
            and state_name == self._current_state.state_name
        ):
            raise StateError(
                "Cannot unload an actively running state.",
                last_state=self._last_state,
                **kwargs,
            )

        cls_ref = self._states[state_name].__class__
        del self._states[state_name]
        return cls_ref
