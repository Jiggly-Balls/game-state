from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING, Generic, TypeVar

from .errors import StateError, StateLoadError
from .state import State
from .utils import MISSING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from inspect import Signature
    from typing import (
        Any,
        Dict,
        List,
        NoReturn,
        Optional,
        Tuple,
        Type,
    )

    from pygame import Surface

    from .utils import StateArgs


__all__ = ("StateManager",)


S = TypeVar("S", bound="State[Any]")

_GLOBAL_ON_SETUP_ARGS: int = 1  # TODO: Remove this in later version.
_GLOBAL_ON_ENTER_ARGS: int = 2
_GLOBAL_ON_LEAVE_ARGS: int = 2
_GLOBAL_ON_LOAD_ARGS: int = 2
_GLOBAL_ON_UNLOAD_ARGS: int = 2
_KW_CONSIDER: Tuple[str, str] = ("VAR_KEYWORD", "KEYWORD_ONLY")


class StateManager(Generic[S]):
    r"""The State Manager used for managing multiple State(s).

    :param window:
        .. deprecated:: 2.3.0

            | To add class attributes to your own state system, make a base state
                (with your custom attributes) and make all your states inherit from it.
                Check the official guide for more info.

        .. versionadded:: 1.0

        The main game window.
    :param bound_state_type:
        The base state class which all states inherits from.
    :type bound_state_type: type[State]
    :param \**kwargs:
        The keyword arguments to bind to ``bound_state_type``.

    :attributes:
        is_running: :class:`bool`
            .. versionadded:: 2.0

            A bool for controlling the game loop. ``True`` by default.
    """

    def __init__(
        self,
        window: Surface = MISSING,
        *,
        bound_state_type: Type[S] = State,
        **kwargs: Any,
    ) -> None:
        # TODO: ADD DEPRECATION WARNING FOR `window`

        self.bound_state_type: Type[S] = bound_state_type
        self.bound_state_type.window = window
        self.bound_state_type.manager = self  # pyright: ignore[reportAttributeAccessIssue]

        for name, value in kwargs.items():
            setattr(self.bound_state_type, name, value)

        self.is_running: bool = True

        # fmt: off
        self._global_on_setup: Optional[Callable[[S], None]] = None
        self._global_on_enter: Optional[Callable[[S, Optional[S]], None]] = None
        self._global_on_leave: Optional[Callable[[Optional[S], S], None]] = None
        self._global_on_load: Optional[Callable[[S, bool], None]] = None
        # fmt: on

        self._lazy_states: Dict[
            str, Tuple[Type[S], Optional[List[StateArgs]]]
        ] = {}
        self._states: Dict[str, S] = {}
        self._current_state: Optional[S] = None
        self._last_state: Optional[S] = None
        self._is_reloading: bool = False

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
    def current_state(self) -> Optional[S]:
        r"""The current state if applied. Will be ``None`` otherwise.

        :type: :class:`State` | :class:`None`

        .. versionchanged:: 2.0

            | Changed from method to property.

        .. note::

            This is a read-only attribute. To change states use
            :meth:`change_state` instead.
        """
        return self._current_state

    @current_state.setter
    def current_state(self, _: Any) -> NoReturn:
        raise ValueError(
            "Cannot overwrite the current state. Use `StateManager.change_state` instead."
        )

    @property
    def last_state(self) -> Optional[S]:
        r"""The last state object if any. Will be ``None`` otherwise

        :type: State | None

        .. versionchanged:: 2.0

            | Changed from method to property.

        .. note::

            This is a read-only attribute.
        """
        return self._last_state

    @last_state.setter
    def last_state(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the last state.")

    @property
    def lazy_state_map(
        self,
    ) -> Dict[str, Tuple[Type[S], Optional[List[StateArgs]]]]:
        r"""A dictionary copy of all the added lazy state names mapped to their respective
        type and state args.

        :type: dict[str, tuple[type[State], None | list[StateArgs]]]

        .. versionadded:: 2.2

        .. note::

            This is a read-only attribute.

        .. note::

            Once the lazy state has been fully initialized, it will be removed from the
            lazy state map.
        """
        return self._lazy_states.copy()

    @lazy_state_map.setter
    def lazy_state_map(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the lazy state map.")

    @property
    def state_map(self) -> Dict[str, S]:
        r"""A dictionary copy of all the state names mapped to their respective instance.

        :type: dict[str, State]

        .. versionchanged:: 2.0

            | Changed from method to property.

        .. versionadded:: 1.0

        .. note::

            This is a read-only attribute.
        """
        return self._states.copy()

    @state_map.setter
    def state_map(self, _: Any) -> NoReturn:
        raise ValueError("Cannot overwrite the state map.")

    @property
    def global_on_enter(
        self,
    ) -> Optional[Callable[[S, Optional[S]], None]]:
        r"""The global on_enter listener called right before a state's on_enter listener.

        :type: None | typing.Callable[[State, typing.Optional[State]], None]

        .. versionchanged:: 2.0.3

            | Global listeners can accept :class:`None` now.

        .. versionadded:: 2.0

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


            your_manager_instance.global_on_enter = global_on_enter
        """

        return self._global_on_enter

    @global_on_enter.setter
    def global_on_enter(
        self, value: Optional[Callable[[S, Optional[S]], None]]
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
    ) -> Optional[Callable[[Optional[S], S], None]]:
        r"""The global on_leave listener called right before a state's on_leave listener.

        :type: None | typing.Callable[[typing.Optional[State], State], None]

        .. versionchanged:: 2.0.3

            | Global listeners can accept :class:`None` now.

        .. versionadded:: 2.0

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


            your_manager_instance.global_on_leave = global_on_leave
        """

        return self._global_on_leave

    @global_on_leave.setter
    def global_on_leave(
        self, value: Optional[Callable[[Optional[S], S], None]]
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
    def global_on_setup(self) -> Optional[Callable[[S], None]]:
        r"""The global ``on_setup`` function for all states.

        :type: None | typing.Callable[[State], None]

        .. deprecated:: 2.3.0

            | Use :meth:`global_on_load` instead.

        .. versionchanged:: 2.0.3

            | Global listeners can accept :class:`None` now.

        .. versionadded:: 2.0

        .. note::

            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        setup.

        Example for a ``global_on_setup`` function-

        .. code-block:: python

            def global_on_setup(state: State) -> None:
                print(f"GLOBAL SETUP - Setting up state: {state.state_name}")


            your_manager_instance.global_on_setup = global_on_setup
        """

        return self._global_on_setup

    @global_on_setup.setter
    def global_on_setup(self, value: Optional[Callable[[S], None]]) -> None:
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
    def global_on_load(self) -> Optional[Callable[[S, bool], None]]:
        r"""The global :meth:`State.on_load` function for all states.

        :type: None | typing.Callable[[State, bool], None]

        .. versionadded:: 2.3

        .. note::

            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        setup.

        Example for a ``global_on_load`` function-

        .. code-block:: python

            def global_on_load(state: State, reload: bool) -> None:
                print(f"GLOBAL LOAD - Loading up state: {state.state_name}")
                if reload:
                    print("The state is being reloaded.")
                else:
                    print("The state is not being reloaded.")


            your_manager_instance.global_on_load = global_on_load
        """

        return self._global_on_load

    @global_on_load.setter
    def global_on_load(
        self, value: Optional[Callable[[S, bool], None]]
    ) -> None:
        if value:
            on_setup_signature = inspect.signature(value)
            pos_args = self._get_pos_args(on_setup_signature)
            kw_args = self._get_kw_args(on_setup_signature)

            if (
                len(on_setup_signature.parameters) != _GLOBAL_ON_LOAD_ARGS
                or kw_args != 0
            ):
                raise TypeError(
                    f"Expected {_GLOBAL_ON_LOAD_ARGS} positional argument(s) only "
                    f"for the function to be assigned to global_on_load. "
                    f"Instead got {pos_args} positional argument(s)"
                    + (
                        f" and {kw_args} keyword argument(s)."
                        if kw_args > 0
                        else "."
                    )
                )

        self._global_on_load = value

    @property
    def global_on_unload(self) -> Optional[Callable[[S, bool], None]]:
        r"""The global :meth:`State.on_unload` function for all states.

        :type: None | typing.Callable[[State, bool], None]

        .. versionadded:: 2.3

        .. note::

            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        setup.

        Example for a ``global_on_unload`` function-

        .. code-block:: python

            def global_on_unload(state: State, reload: bool) -> None:
                print(f"GLOBAL UNLOAD - Loading up state: {state.state_name}")
                if reload:
                    print("The state is being reloaded.")
                else:
                    print("The state is not being reloaded.")


            your_manager_instance.global_on_unload = global_on_unload
        """

        return self._global_on_load

    @global_on_unload.setter
    def global_on_unload(
        self, value: Optional[Callable[[S, bool], None]]
    ) -> None:
        if value:
            on_unload_signature = inspect.signature(value)
            pos_args = self._get_pos_args(on_unload_signature)
            kw_args = self._get_kw_args(on_unload_signature)

            if (
                len(on_unload_signature.parameters) != _GLOBAL_ON_LOAD_ARGS
                or kw_args != 0
            ):
                raise TypeError(
                    f"Expected {_GLOBAL_ON_UNLOAD_ARGS} positional argument(s) only "
                    f"for the function to be assigned to global_on_unload. "
                    f"Instead got {pos_args} positional argument(s)"
                    + (
                        f" and {kw_args} keyword argument(s)."
                        if kw_args > 0
                        else "."
                    )
                )

        self._global_on_load = value

    def change_state(self, state_name: str) -> None:
        r"""Changes the current state and updates the last state. This method executes
        the :meth:`State.on_leave` & :meth:`State.on_enter` state & global listeners
        (:meth:`global_on_leave` & :meth:`global_on_enter`)

        .. versionadded:: 1.0

        :param state_name:
            | The name of the State you want to switch to.

        :raises:
            :exc:`game_state.errors.StateError`
                | Raised when the state name doesn't exist in the manager.
        """

        if state_name not in self._states:
            if state_name in self._lazy_states:
                fetched_lazy_state, lazy_state_args = self._lazy_states[
                    state_name
                ]
                self.load_states(
                    fetched_lazy_state, state_args=lazy_state_args
                )
                del self._lazy_states[state_name]

            else:
                state_keys = self.state_map.keys()
                lazy_state_keys = self.lazy_state_map.keys()
                message = (
                    f"State `{state_name}` isn't present from the available"
                )

                if len(state_keys) == 0 and len(lazy_state_keys) == 0:
                    message = "No states have been loaded to change to."

                if len(state_keys) > 0:
                    message += f" states: `{', '.join(self.state_map.keys())}`"

                if len(lazy_state_keys) > 0:
                    if len(state_keys) > 0:
                        message += " and "
                    message += f"from the available lazy states: `{', '.join(self.lazy_state_map.keys())}`"

                raise StateError(
                    message,
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

        .. versionadded:: 1.0

        :param path:
            | The path to the State file containing the hook function to be called.
        :param \**kwargs:
            | The keyword arguments to be passed to the hook function.

        :raises:
            :exc:`game_state.errors.StateError`
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

    def add_lazy_states(
        self,
        *lazy_states: Type[S],
        force: bool = False,
        state_args: Optional[Iterable[StateArgs]] = None,
    ) -> None:
        r"""Lazily adds the States into the StateManager.
        Unlike :meth:`load_states`, it only initializes the state when required
        i.e. when :meth:`change_state` switches to the lazy state.

        .. versionadded:: 2.2

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
            :exc:`game_state.errors.StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.

            :exc:`game_state.errors.StateLoadError`
                | Raised when the passed argument(s) is not subclassed from ``State``.
        """

        args_cache: Dict[str, Optional[StateArgs]] = {}
        all_states: List[Type[S]] = self.bound_state_type._lazy_states.copy()  # pyright: ignore[reportPrivateUsage, reportAssignmentType]
        all_states.extend(lazy_states)
        self.bound_state_type._lazy_states.clear()  # pyright: ignore[reportPrivateUsage]

        if state_args:
            for argument in state_args:
                args_cache[argument.state_name] = argument

        for lazy_state in all_states:
            if (
                not force
                and lazy_state.state_name in self._states
                or lazy_state.state_name in self._lazy_states
            ):
                raise StateLoadError(
                    f"State: {lazy_state.state_name} has already been added.",
                    last_state=self._last_state,
                )

            lazy_state_arg: Optional[List[StateArgs]] = (  # pyright: ignore[reportAssignmentType]
                None
                if args_cache.get(lazy_state.state_name) is None
                else [args_cache[lazy_state.state_name]]
            )
            self._lazy_states[lazy_state.state_name] = (
                lazy_state,
                lazy_state_arg,
            )

    def load_states(
        self,
        *states: Type[S],
        force: bool = False,
        state_args: Optional[Iterable[StateArgs]] = None,
    ) -> None:
        r"""Loads the States into the StateManager.

        .. versionchanged:: 2.1

            | Method now accepts ``state_args``.

        .. versionadded:: 1.0

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
            :exc:`game_state.errors.StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.
        """

        args_cache: Dict[str, Dict[str, Any]] = {}
        all_states: List[Type[S]] = self.bound_state_type._eager_states.copy()  # pyright: ignore[reportPrivateUsage, reportAssignmentType]
        all_states.extend(states)
        self.bound_state_type._eager_states.clear()  # pyright: ignore[reportPrivateUsage]

        if state_args:
            for argument in state_args:
                args_cache[argument.state_name] = argument.get_data()

        for state in all_states:
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
                # TODO: ADD DEPRECATION WARNING

            if self._global_on_load:
                self._global_on_load(
                    self._states[state.state_name], self._is_reloading
                )

            self._states[
                state.state_name
            ].on_setup()  # TODO: Remove in later versions
            self._states[state.state_name].on_load(self._is_reloading)

    def reload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> S:
        r"""Reloads the specified State. A short hand to :meth:`unload_state` &
        :meth:`load_states`.

        .. versionadded:: 1.0

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
            :exc:`game_state.errors.StateLoadError`
                | Raised when the state has already been loaded.
                | Only raised when ``force`` is set to ``False``.
        """
        if state_name not in self._states:
            state_keys = self.state_map.keys()
            lazy_state_keys = self.lazy_state_map.keys()

            message = f"State: `{state_name}` doesn't exist to be unloaded"

            if len(state_keys) == 0 and len(lazy_state_keys) == 0:
                message = f"No state has been loaded to unload `{state_name}`."

            if len(state_keys) > 0:
                message += (
                    f" from the following states: `{', '.join(state_keys)}`"
                )

            if state_name in lazy_state_keys:
                message += (
                    "; but exists as a lazy state. "
                    "Did you mean to use `StateManager.remove_lazy_state` instead?"
                )

            raise StateLoadError(
                message,
                last_state=self._last_state,
                **kwargs,
            )

        self._is_reloading = True
        deleted_cls = self.unload_state(
            state_name=state_name, force=force, **kwargs
        )
        self.load_states(deleted_cls, force=force, **kwargs)
        self._is_reloading = False

        return self._states[state_name]

    def remove_lazy_state(
        self, state_name: str
    ) -> Optional[Tuple[Type[S], Optional[List[StateArgs]]]]:
        r"""Removes the specified lazy state from the :class:`StateManager`. This will
        silently fail if the lazy state has been loaded to the manager, which in case
        you will have to unload via :meth:`unload_state

        .. versionadded:: 2.2

        :param state_name:
            | The state to be removed from the manager.

        :returns:
            | Either returns :class:`None` if the lazy state was not found or it returns a
            | tuple with the first element being the lazy state and the second being
            | the :class:`StateArgs` if any were passed.
        """

        try:
            cls_ref = self._lazy_states[state_name]
            del self._lazy_states[state_name]
            return cls_ref
        except KeyError:
            return None

    def unload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> Type[S]:
        r"""Unloads the specified state from the :class:`StateManager`.

        .. versionadded:: 1.0

        :param state_name:
            | The state name to be unloaded from the manager.

        :param force:
            | Default ``False``.
            |
            | Unloads the State even if it's an actively running State without raising any
              internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :returns:
            | The :class:`State` class of the deleted State name.

        :raises:
            :exc:`game_state.errors.StateLoadError`
                | Raised when the state doesn't exist in the manager to be unloaded.

            :exc:`game_state.errors.StateError`
                | Raised when trying to unload an actively running State.
                | Only raised when ``force`` is set to ``False``.
        """

        if state_name not in self._states:
            state_keys = self.state_map.keys()
            lazy_state_keys = self.lazy_state_map.keys()

            message = f"State: `{state_name}` doesn't exist to be unloaded"

            if len(state_keys) == 0 and len(lazy_state_keys) == 0:
                message = f"No state has been loaded to unload `{state_name}`."

            if len(state_keys) > 0:
                message += (
                    f" from the following states: `{', '.join(state_keys)}`"
                )

            if state_name in lazy_state_keys:
                message += (
                    "; but exists as a lazy state. "
                    "Did you mean to use `StateManager.remove_lazy_state` instead?"
                )

            raise StateLoadError(
                message,
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

        self._states[state_name].on_unload(self._is_reloading)
        cls_ref = self._states[state_name].__class__
        del self._states[state_name]
        return cls_ref
