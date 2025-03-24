from __future__ import annotations

import importlib

from typing import TYPE_CHECKING

from .errors import (
    StateError,
    StateLoadError,
    ExitState,
    ExitGame,
)
from .state import State

if TYPE_CHECKING:
    from pygame import Surface
    from typing import Any, Dict, NoReturn, Optional, Type


class StateManager:
    """The State Manager used for managing multiple State(s).

    :param window:
        The main game window.
    """

    __slots__ = (
        "_states",
        "_current_state",
        "_last_state",
    )

    def __init__(self, window: Surface) -> None:
        State.window = window
        State.manager = self

        self._states: Dict[str, State] = {}
        self._current_state: Optional[State] = None
        self._last_state: Optional[State] = None

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
            |
            | **WARNING: If set to** ``True`` **it may lead to unexpected behavior.**

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
            self._states[state.state_name].setup()

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
            |
            | **WARNING: If set to** ``True`` **it may lead to unexpected behavior.**

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
            |
            | **WARNING: If set to** ``True`` **it may lead to unexpected behavior.**

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

    def get_current_state(self) -> Optional[State]:
        """Gets the current State instance.

        :returns:
            | Returns the current State instance.
        """

        return self._current_state

    def get_last_state(self) -> Optional[State]:
        """Gets the previous State instance.

        :returns:
            | Returns the previous State instance.
        """

        return self._last_state

    def get_state_map(self) -> Dict[str, State]:
        """Gets the dictionary copy of all states.

        :returns:
            | Returns the dictionary copy of all states.
        """

        return self._states.copy()

    def change_state(self, state_name: str) -> None:
        """Changes the current state and updates the last state.

        :param state_name:
            | The name of the State you want to switch to.

        :raises:
            :exc:`AssertionError`
                | Raised when the state name doesn't exist in the manager.
        """

        assert (
            state_name in self._states
        ), f"State `{state_name}` isn't present from the available states: "
        f"`{', '.join(self.get_state_map().keys())}`."

        self._last_state = self._current_state
        self._current_state = self._states[state_name]

    def update_state(self, **kwargs: Any) -> NoReturn:
        r"""Updates the changed State to take place.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :raises:
            :exc:`ExitState`
                | Raised when the state has successfully exited.

            :exc:`StateError`
                | Raised when the current state is ``None`` i.e having no State to update to.
        """

        if self._current_state is not None:
            raise ExitState(
                "State has successfully exited.",
                last_state=self._last_state,
                **kwargs,
            )
        raise StateError(
            "No state has been set to exit from.",
            last_state=self._last_state,
            **kwargs,
        )

    def run_state(self, **kwargs: Any) -> None:
        r"""The entry point to running the StateManager. To be only called once. For
        changing ``State``\s use ``StateManager.change_state`` & ``StateManager.update_state``

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :raises:
            :exc:`StateError`
                | Raised when the current state is ``None`` i.e having no State to run.
        """

        if self._current_state is not None:
            self._current_state.run()
        else:
            raise StateError(
                "No state has been set to run.",
                last_state=self._last_state,
                **kwargs,
            )

    def exit_game(self, **kwargs: Any) -> NoReturn:
        r"""Exits the entire game.

        :param \**kwargs:
            | The keyword arguments to be passed on to the raised errors.

        :raises:
            :exc:`ExitGame`
                | Raised when the state has successfully exited.
        """

        raise ExitGame(
            "Game has successfully exited.",
            last_state=self._last_state,
            **kwargs,
        )
