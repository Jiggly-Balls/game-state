from __future__ import annotations

import importlib
import inspect
import logging
from typing import TYPE_CHECKING, Generic, TypeVar, overload

from ..errors import OverlayError, StateError, StateLoadError
from .state import State

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
        Union,
    )

    from ..utils import StateArgs


__all__ = ("StateManager",)
logger = logging.getLogger(__name__)


S = TypeVar("S", bound="State[Any]")

_GLOBAL_ON_ENTER_ARGS: int = 2
_GLOBAL_ON_LEAVE_ARGS: int = 2
_GLOBAL_ON_LOAD_ARGS: int = 2
_GLOBAL_ON_UNLOAD_ARGS: int = 2
_KW_CONSIDER: Tuple[str, str] = ("VAR_KEYWORD", "KEYWORD_ONLY")


class StateManager(Generic[S]):
    r"""
    The State Manager used for managing multiple State(s).

    :param bound_state_type:
        | The base state class which all states inherit from.
    :type bound_state_type: type[State]
    :param \**kwargs:
        | The keyword arguments to bind to ``bound_state_type``.

    :attributes:
        is_running: :class:`bool`
            .. versionadded:: 2.0

            A bool for controlling the game loop. ``True`` by default.
    """

    def __init__(
        self,
        *,
        bound_state_type: Type[S] = State,
        **kwargs: Any,
    ) -> None:
        self.bound_state_type: Type[S] = bound_state_type
        self.bound_state_type.manager = self  # pyright: ignore[reportAttributeAccessIssue]

        for name, value in kwargs.items():
            setattr(self.bound_state_type, name, value)

        self.is_running: bool = True

        # fmt: off
        self._global_on_enter: Optional[Callable[[S, Optional[S]], None]] = None
        self._global_on_leave: Optional[Callable[[Optional[S], S], None]] = None
        self._global_on_load: Optional[Callable[[S, bool], None]] = None
        # fmt: on

        self._lazy_states: Dict[
            str, Tuple[Type[S], Optional[List[StateArgs]]]
        ] = {}
        self._states: Dict[str, S] = {}
        self._last_state: Optional[S] = None
        self._is_reloading: bool = False

        self._state_stack: List[S] = []
        self._is_temp: Dict[S, bool] = {}
        self._overlay_map: Dict[str | int, S] = {}
        self._last_id: int = 0

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
        r"""
        The current state if applied. Will be ``None`` otherwise.

        :type: :class:`State` | :class:`None`

        .. versionchanged:: 2.0

            | Changed from method to property.

        .. note::

            This is a read-only attribute. To change states use
            :meth:`change_state` instead.
        """
        return self._state_stack[-1] if self._state_stack else None

    @current_state.setter
    def current_state(self, _: Any) -> NoReturn:
        msg = "Cannot overwrite the current state. Use `StateManager.change_state` instead."
        raise ValueError(msg)

    @property
    def last_state(self) -> Optional[S]:
        r"""
        The last state object if any. Will be ``None`` otherwise.

        :type: State | None

        .. versionchanged:: 2.0

            | Changed from method to property.

        .. note::

            This is a read-only attribute.
        """
        return self._last_state

    @last_state.setter
    def last_state(self, _: Any) -> NoReturn:
        msg = "Cannot overwrite the last state."
        raise ValueError(msg)

    @property
    def lazy_state_map(
        self,
    ) -> Dict[str, Tuple[Type[S], Optional[List[StateArgs]]]]:
        r"""
        A dictionary copy of all the added lazy state names mapped to their respective
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
        msg = "Cannot overwrite the lazy state map."
        raise ValueError(msg)

    @property
    def state_map(self) -> Dict[str, S]:
        r"""
        A dictionary copy of all the state names mapped to their respective instance.

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
        msg = "Cannot overwrite the state map."
        raise ValueError(msg)

    @property
    def global_on_enter(
        self,
    ) -> Optional[Callable[[S, Optional[S]], None]]:
        r"""
        The global on_enter listener called right before a state's on_enter listener.

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
        r"""
        The global on_leave listener called right before a state's on_leave listener.

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
    def global_on_load(self) -> Optional[Callable[[S, bool], None]]:
        r"""
        The global :meth:`State.on_load` function for all states.

        :type: None | typing.Callable[[State, bool], None]

        .. versionadded:: 2.3

        .. note::

            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        set up.

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
        r"""
        The global :meth:`State.on_unload` function for all states.

        :type: None | typing.Callable[[State, bool], None]

        .. versionadded:: 2.3

        .. note::

            This has to be assigned before loading the states into the manager.

        The first argument passed to the function is the current state which has been
        set up.

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

    def _validate_states(self, state_name: str) -> None:
        if state_name not in self._states:
            if state_name in self._lazy_states:
                logger.debug("Loading lazy state: %s", state_name)

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

                if len(state_keys) == -1 and len(lazy_state_keys) == 0:
                    message = "No states have been loaded to change to."

                if len(state_keys) > -1:
                    message += f" states: `{', '.join(self.state_map.keys())}`"

                if len(lazy_state_keys) > -1:
                    if len(state_keys) > -1:
                        message += " and "
                    message += f"from the available lazy states: `{', '.join(self.lazy_state_map.keys())}`"

                raise StateError(
                    message,
                    last_state=self._last_state,
                )

    def _handle_events(self) -> None:
        if self._global_on_leave:
            logger.debug("Calling global_on_leave")
            self._global_on_leave(self._last_state, self.current_state)  # pyright: ignore[reportArgumentType]

        if self._last_state:
            logger.debug("Calling %s.on_leave", self._last_state.state_name)
            self._last_state.on_leave(self.current_state)

        if self._global_on_enter:
            logger.debug("Calling global_on_enter")
            self._global_on_enter(self.current_state, self._last_state)  # pyright: ignore[reportArgumentType]

        if self.current_state:
            logger.debug("Calling %s.on_enter", self.current_state.state_name)
            self.current_state.on_enter(self._last_state)

    def change_state(self, state_name: str) -> None:
        r"""
        Changes the current state and updates the last state. This method executes
        the :meth:`State.on_leave` & :meth:`State.on_enter` state & global listeners
        (:meth:`global_on_leave` & :meth:`global_on_enter`).

        .. versionadded:: 1.0

        :param state_name:
            | The name of the state you want to switch to.

        :raises:
            :exc:`game_state.errors.StateError`
                | Raised when the state name doesn't exist in the manager.
        """
        self._validate_states(state_name)

        logger.debug(
            "Changing from state %s to %s",
            getattr(self.current_state, "state_name", "None"),
            state_name,
        )

        self._last_state = self.current_state
        if self._state_stack:
            self._state_stack[0] = self._states[state_name]
        else:
            self._state_stack.append(self._states[state_name])

        self._handle_events()

    def connect_state_hook(self, path: str, **kwargs: Any) -> None:
        r"""
        Calls the hook function of the state file.

        .. versionadded:: 1.0

        :param path:
            | The path to the state file containing the hook function to be called.
        :param \**kwargs:
            | The keyword arguments to be passed to the hook function.

        :raises:
            :exc:`game_state.errors.StateError`
                | Raised when the hook function was not found in the state file to be loaded.
        """
        state = importlib.import_module(path)
        if "hook" not in state.__dict__:
            msg = (
                "\nAn error occurred in loading state path-\n"
                f"`{path}`\n"
                "`hook` function was not found in state file to load.\n"
            )
            raise StateError(
                msg,
                last_state=self._last_state,
                **kwargs,
            )

        logger.debug("Hooking up state: %s", state.__name__)
        state.__dict__["hook"](**kwargs)

    def add_lazy_states(
        self,
        *lazy_states: Type[S],
        force: bool = False,
        state_args: Optional[Iterable[StateArgs]] = None,
    ) -> None:
        r"""
        Lazily adds the States into the StateManager.
        Unlike :meth:`load_states`, it only initializes the state when required
        i.e. when :meth:`change_state` switches to the lazy state.

        .. versionadded:: 2.2

        :param lazy_states:
            | The states to be loaded into the manager as lazy states.
        :type lazy_states: typing.Type[State]

        :param force:
            | Default ``False``.
            |
            | Loads the state regardless of whether the state has already been loaded or not
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
                msg = f"State: {lazy_state.state_name} has already been added."
                raise StateLoadError(
                    msg,
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
            logger.debug("Added lazy state: %s", lazy_state.state_name)

    def load_states(
        self,
        *states: Type[S],
        force: bool = False,
        state_args: Optional[Iterable[StateArgs]] = None,
    ) -> None:
        r"""
        Loads the States into the StateManager.

        .. versionchanged:: 2.1

            | Method now accepts ``state_args``.

        .. versionadded:: 1.0

        :param states:
            | The States to be loaded into the manager.
        :type states: typing.Type[State]

        :param force:
            | Default ``False``.
            |
            | Loads the state regardless of whether the state has already been loaded or not
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
                msg = f"State: {state.state_name} has already been loaded."
                raise StateLoadError(
                    msg,
                    last_state=self._last_state,
                    **final_state_args,
                )

            self._states[state.state_name] = state(**final_state_args)
            if final_state_args:
                self._states[state.state_name].state_args = final_state_args
            logger.debug("Loaded state: %s", state.state_name)

            if self._global_on_load:
                logger.debug("Calling global_on_load")
                self._global_on_load(
                    self._states[state.state_name], self._is_reloading
                )

            logger.debug("Calling %s.on_load", state.state_name)
            self._states[state.state_name].on_load(self._is_reloading)

    def reload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> S:
        r"""
        Reloads the specified state. A shorthand to :meth:`unload_state` &
        :meth:`load_states`.

        .. versionadded:: 1.0

        :param state_name:
            | The state name to be reloaded.

        :param force:
            | Default ``False``.
            |
            | Reloads the state even if it's an actively running state without
            | raising any internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed to the :meth:`unload_state` & :meth:`load_states`.

        :rtype: State

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

        logger.debug("Reloading state: %s", state_name)

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
        r"""
        Removes the specified lazy state from the :class:`StateManager`. This will
        silently fail if the lazy state has been loaded to the manager, which in case
        you will have to unload via :meth:`unload_state`.

        .. versionadded:: 2.2

        :param state_name:
            | The state to be removed from the manager.

        :rtype: None | typing.Tuple[typing.Type[State], typing.Optional[typing.List[StateArgs]]]

        :returns:
            | Either returns :class:`None` if the lazy state was not found, or it returns a
            | tuple with the first element being the lazy state and the second being
            | the :class:`StateArgs` if any were passed.
        """
        try:
            cls_ref = self._lazy_states[state_name]
            del self._lazy_states[state_name]
            logger.debug("Successfully removed lazy state: %s", state_name)
        except KeyError:
            logger.exception("Failed to remove lazy state: %s", state_name)
            return None
        else:
            return cls_ref

    def unload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> Type[S]:
        r"""
        Unloads the specified state from the :class:`StateManager`.

        .. versionadded:: 1.0

        :param state_name:
            | The state name to be unloaded from the manager.

        :param force:
            | Default ``False``.
            |
            | Unloads the state even if it's an actively running state without raising any
              internal error.

            .. warning::
              If set to ``True`` it may lead to unexpected behavior.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :rtype: typing.Type[State]

        :returns:
            | The :class:`State` class of the deleted state name.

        :raises:
            :exc:`game_state.errors.StateLoadError`
                | Raised when the state doesn't exist in the manager to be unloaded.

            :exc:`game_state.errors.StateError`
                | Raised when trying to unload an actively running state.
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

        if (
            not force
            and self.current_state is not None
            and state_name == self.current_state.state_name
        ):
            msg = "Cannot unload an actively running state."
            raise StateError(
                msg,
                last_state=self._last_state,
                **kwargs,
            )

        logger.debug("Calling %s.on_unload", state_name)
        self._states[state_name].on_unload(self._is_reloading)

        cls_ref = self._states[state_name].__class__
        del self._states[state_name]
        logger.debug("Successfully unloaded state: %s", state_name)

        return cls_ref

    def close_overlay(self, state_id: Union[int, str], **kwargs: Any) -> None:
        r"""
        Closes an overlay state. You can close any of the opened overlay state
        and not just the active overlay state.

        .. versionadded:: 2.5

        :param state_id:
            | The state ID with which it was opened with. This is **not** the state name.

            .. note::
              It's recommended to use a string rather than an integer when assigning
              a custom ID. When no ID is supplied, the manager defaults to an
              incremental integer counter for its overlay elements, which can conflict
              with custom integer IDs.

            .. note::
              Only the following state listeners will execute upon calling this method:

              - :meth:`State.on_overlay_leave` on the current active overlay.
              - :meth:`State.on_overlay_enter` for the previous active overlay, if any.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :raises:
            :exc:`game_state.errors.OverlayError`
                | Raised when no state of ``state_id`` was found to close.
        """
        if state_id not in self._overlay_map:
            msg = f"Could not find overlay state of ID `{state_id}` ({type(state_id)})"
            raise OverlayError(msg, **kwargs)

        overlay_ref = self._overlay_map[state_id]
        overlay_ref.state_id = None
        overlay_ref.on_overlay_leave(self._is_temp[overlay_ref])

        del self._overlay_map[state_id]
        del self._is_temp[overlay_ref]
        self._state_stack.remove(overlay_ref)

    def close_all_overlays(self) -> None:
        r"""
        Closes all opened overlay states.

        .. versionadded:: 2.5

        .. note::
          Only the following state listener executes upon calling this method:

          - :meth:`State.on_overlay_leave` on the current active overlay.

          For all overlay states, this is called in order from most recently opened to
          first opened.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        """
        if len(self._state_stack) > 1:
            original_state = self._state_stack.pop(0)
            for state in self._state_stack:
                state.on_overlay_leave(self._is_temp[state])
                state.state_id = None
            self._state_stack.clear()
            self._is_temp.clear()
            self._overlay_map.clear()
            self._state_stack.append(original_state)

    @overload
    def open_overlay(
        self,
        state_name: str,
        state_id: int,
    ) -> int: ...

    @overload
    def open_overlay(
        self,
        state_name: str,
        state_id: str,
    ) -> str: ...

    @overload
    def open_overlay(
        self,
        state_name: str,
        state_id: None = ...,
    ) -> int: ...

    def open_overlay(
        self,
        state_name: str,
        state_id: Optional[Union[int, str]] = None,
    ) -> Union[int, str]:
        self._validate_states(state_name)

        if state_id is None:
            state_id = self._last_id
            self._last_id += 1

        if state_id in self._overlay_map:
            msg = "Duplicate ID for overlay state found."
            raise OverlayError(msg)

        state = self._states[state_name]
        if state in self._state_stack:
            temporary = True
            final_state = state.__class__(**(state.state_args or {}))
        else:
            temporary = False
            final_state = state

        final_state.state_id = state_id
        self._state_stack.append(final_state)
        self._overlay_map[state_id] = final_state
        self._is_temp[final_state] = temporary

        final_state.on_overlay_enter(temporary)

        return state_id
