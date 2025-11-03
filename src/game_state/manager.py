from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING

from .errors import StateError, StateLoadError
from .state import State

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from inspect import Signature
    from typing import Any, Dict, NoReturn, Optional, Tuple, Type

    from pygame import Surface

    from .utils import StateArgs


__all__ = ("StateManager",)


_GLOBAL_ON_SETUP_ARGS: int = 1
_GLOBAL_ON_ENTER_ARGS: int = 2
_GLOBAL_ON_LEAVE_ARGS: int = 2
_KW_CONSIDER: Tuple[str, str] = ("VAR_KEYWORD", "KEYWORD_ONLY")


class StateManager:
    """The State Manager used for managing multiple State(s).

    :param window:
        The main game window.

    :attributes:
        is_running: :class:`bool`
            A bool for controlling the game loop. ``True`` by default.
    """

    def __init__(self, window: Surface) -> None:
        State.window = window
        State.manager = self

        self.is_running: bool = True

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

    def _get_kw_args(self, signature: Signature) -> int:
        amount = 0
        for param in signature.parameters.values():
            if param.kind in _KW_CONSIDER:
                amount += 1
        return amount

    def _get_pos_args(self, signature: Signature) -> int:
        amount = 0
        for param in signature.parameters.values():
            if param.kind not in _KW_CONSIDER:
                amount += 1
        return amount

    @property
    def current_state(self) -> Optional[State]:
        """The current state if applied. Will be ``None`` otherwise.

        .. note::
            This is a read-only attribute. To change states use
            ``StateManger.change_state`` instead.
        """
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
        """The global on_enter listener called right before a state's on_enter listener.

        .. note::
            This has to be assigned before changing the states.

        The first argument passed to the function is the current state and the second
        is the previous state which may be ``None``.

        Example for a ``global_on_enter`` function-

        .. code-block:: python

            def global_on_enter(
                current_state: State, previous_state: None | State
            ) -> None:
                if previous_state:
                    print(
                        f"GLOBAL ENTER - Entering {current_state.state_name} from {previous_state.state_name}"
                    )
        """
        return self._global_on_enter

    @global_on_enter.setter
    def global_on_enter(
        self, value: Optional[Callable[[State, Optional[State]], None]]
    ) -> None:
        if value:
            on_enter_signature = inspect.signature(value)
            pos_args = self._get_pos_args(on_enter_signature)
            kw_args = self._get_kw_args(on_enter_signature)

            if (
                len(on_enter_signature.parameters) != _GLOBAL_ON_ENTER_ARGS
                or kw_args != 0
            ):
                raise TypeError(
                    f"Expected {_GLOBAL_ON_ENTER_ARGS} positional argument(s) only "
                    f"for the function to be assigned to global_on_enter. "
                    f"Instead got {pos_args} positional argument(s)"
                    + (
                        f" and {kw_args} keyword argument(s)."
                        if kw_args > 0
                        else "."
                    )
                )

        self._global_on_enter = value

    @property
    def global_on_leave(
        self,
    ) -> Optional[Callable[[Optional[State], State], None]]:
        """The global on_leave listener called right before a state's on_leave listener.

        .. note::
            This has to be assigned before changing the states.

        The first argument passed to the function is the current state which may be
        ``None`` and the second is the next state to take place.

        Example for a ``global_on_leave`` function-

        .. code-block:: python

            def global_on_leave(
                current_state: None | State, next_state: State
            ) -> None:
                if current_state:
                    print(
                        f"GLOBAL LEAVE - Leaving {current_state.state_name} to {next_state.state_name}"
                    )
        """
        return self._global_on_leave

    @global_on_leave.setter
    def global_on_leave(
        self, value: Optional[Callable[[Optional[State], State], None]]
    ) -> None:
        if value:
            on_leave_signature = inspect.signature(value)
            pos_args = self._get_pos_args(on_leave_signature)
            kw_args = self._get_kw_args(on_leave_signature)

            if (
                len(on_leave_signature.parameters) != _GLOBAL_ON_LEAVE_ARGS
                or kw_args != 0
            ):
                raise TypeError(
                    f"Expected {_GLOBAL_ON_LEAVE_ARGS} positional argument(s) only "
                    f"for the function to be assigned to global_on_leave. "
                    f"Instead got {pos_args} positional argument(s)"
                    + (
                        f" and {kw_args} keyword argument(s)."
                        if kw_args > 0
                        else "."
                    )
                )

        self._global_on_leave = value

    @property
    def global_on_setup(self) -> Optional[Callable[[State], None]]:
        """The global ``on_setup`` function for all states.

        .. note::
            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        setup.

        Example for a ``global_on_setup`` function-

        .. code-block:: python

            def global_setup(state: State) -> None:
                print(f"GLOBAL SETUP - Setting up state: {state.state_name}")
        """
        return self._global_on_setup

    @global_on_setup.setter
    def global_on_setup(
        self, value: Optional[Callable[[State], None]]
    ) -> None:
        if value:
            on_setup_signature = inspect.signature(value)
            pos_args = self._get_pos_args(on_setup_signature)
            kw_args = self._get_kw_args(on_setup_signature)

            if (
                len(on_setup_signature.parameters) != _GLOBAL_ON_SETUP_ARGS
                or kw_args != 0
            ):
                raise TypeError(
                    f"Expected {_GLOBAL_ON_SETUP_ARGS} positional argument(s) only "
                    f"for the function to be assigned to global_on_setup. "
                    f"Instead got {pos_args} positional argument(s)"
                    + (
                        f" and {kw_args} keyword argument(s)."
                        if kw_args > 0
                        else "."
                    )
                )

        self._global_on_setup = value

    @property
    def last_state(self) -> Optional[State]:
        """The last state object if any. Will be ``None`` otherwise

        .. note::
            This is a read-only attribute.
        """
        return self._last_state

    @last_state.setter
    def last_state(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the last state.")

    @property
    def state_map(self) -> Dict[str, State]:
        """A dictionary copy of all the state names mapped to their respective instance.

        .. note::
            This is a read-only attribute.
        """
        return self._states.copy()

    @state_map.setter
    def state_map(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the state map.")

    def change_state(self, state_name: str) -> None:
        """Changes the current state and updates the last state. This method executes
        the ``on_leave`` & ``on_enter`` state & global listeners.

        :param state_name:
            | The name of the State you want to switch to.

        :raises:
            :exc:`StateError`
                | Raised when the state name doesn't exist in the manager.
        """

        if state_name not in self._states:
            raise StateError(
                f"State `{state_name}` isn't present from the available states: "
                f"`{', '.join(self.state_map.keys())}`.",
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
        self,
        *states: Type[State],
        force: bool = False,
        state_args: Optional[Iterable[StateArgs]] = None,
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

        :param state_args:
            | The data to be passed to the subclassed states upon their initialization in the manager.

        :raises:
            :exc:`StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.

            :exc:`StateError`
                | Raised when the passed argument(s) is not subclassed from ``State``.
        """

        args_cache: Dict[str, Dict[str, Any]] = {}

        if state_args:
            for argument in state_args:
                args_cache[argument.state_name] = argument.get_data()

        for state in states:
            if not issubclass(state, State):
                raise StateError(
                    "The passed argument(s) is not a subclass of State.",
                    last_state=self._last_state,
                )

            final_state_args = args_cache.get(state.state_name, {})

            if not force and state.state_name in self._states:
                raise StateLoadError(
                    f"State: {state.state_name} has already been loaded.",
                    last_state=self._last_state,
                    **final_state_args,
                )

            self._states[state.state_name] = state(**final_state_args)
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
