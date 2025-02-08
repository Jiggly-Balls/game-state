from __future__ import annotations

import importlib

from typing import TYPE_CHECKING

from game_state.errors import (
    StateError,
    StateLoadError,
    ExitStateError,
    ExitGameError,
)
from game_state.state import State
from typing import NoReturn, Optional, Dict, Any

if TYPE_CHECKING:
    from pygame import Surface
    from typing import NoReturn, Optional, Dict, Any


class StateManager:
    """The State Manager used for managing multiple State(s)."""

    __slots__ = (
        "__states",
        "__current_state",
        "__last_state",
    )

    def __init__(self, window: Surface) -> None:
        """The State Manager's init.

        :param window:
            The main game window.
        """

        State.window = window
        State.manager = self

        self.__states: Dict[str, State] = {}
        self.__current_state: Optional[State] = None
        self.__last_state: Optional[State] = None

    def connect_state_hook(self, path: str, **kwargs: Any) -> None:
        r"""Calls the hook function of the state file.

        :param path:
            The path to the State file containing the hook function to be called.
        :param \**kwargs:
            The keyword arguments to be passed to the hook function.

        Raises
        ------
        :exc:`StateError`
            Raised when the hook function was not found in the state file to be loaded.
        """

        state = importlib.import_module(path)
        if "hook" not in state.__dict__:
            raise StateError(
                "\nAn error occurred in loading State Path-\n"
                f"`{path}`\n"
                "`hook` function was not found in state file to load.\n",
                last_state=self.__last_state,
                **kwargs,
            )

        state.__dict__["hook"](**kwargs)

    def load_states(
        self, *states: type[State], force: bool = False, **kwargs: Any
    ) -> None:
        r"""Loads the States into the StateManager.

        :param states:
            The States to be loaded into the manager.

        :param force: default `False`
            Loads the State regardless of whether the State has already been loaded or not
            without raising any internal error.

        :param \**kwargs:
            The keyword arguments to be passed to the State's subclass on instantiation.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state has already been loaded.
            Only raised when `force` is set to `False`.
        """

        for state in states:
            if not force and state.__name__ in self.__states:
                raise StateLoadError(
                    f"State: {state.__name__} has already been loaded.",
                    last_state=self.__last_state,
                    **kwargs,
                )

            self.__states[state.__name__] = state(**kwargs)
            self.__states[state.__name__].setup()

    def unload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> type[State]:
        r"""Unloads the `State` from the StateManager.

        :param \*states:
            The States to be loaded into the manager.

        :param force: default `False`
            Unloads the State even if it's an actively running State without raising any
            internal error.
            **WARNING: If set to `True` it may lead to unexpected behavior.**

        :param \**kwargs:
            The keyword arguments to be passed on to the raised errors.

        Returns
        --------
        type[:class:`State`]
            The :class:`State` class of the deleted State name.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state doesn't exist in the manager to be unloaded.

        :exc:`StateError`
            Raised when trying to unload an actively running State.
            Only raised when `force` is set to `False`.
        """

        if state_name not in self.__states:
            raise StateLoadError(
                f"State: {state_name} doesn't exist to be unloaded.",
                last_state=self.__last_state,
                **kwargs,
            )

        elif (
            not force
            and self.__current_state is not None
            and state_name == self.__current_state.__name__
        ):
            raise StateError(
                "Cannot unload an actively running state.",
                last_state=self.__last_state,
                **kwargs,
            )

        cls_ref = self.__states[state_name].__class__
        del self.__states[state_name]
        return cls_ref

    def reload_state(
        self, state_name: str, force: bool = False, **kwargs: Any
    ) -> State:
        r"""Reloads the specified State. A short hand to `StateManager.unload_state` &
        `StateManager.load_state`.

        :param state_name:
            The `State` name to be reloaded.

        :param force: default `False`
            Reloads the State even if it's an actively running State without raising any
            internal error.
            **WARNING: If set to `True` it may lead to unexpected behavior.**

        :param \**kwargs:
            The keyword arguments to be passed to the StateManager.unload_state` & `StateManager.load_state`.

        Returns
        --------
        :class:`State`
            Returns the newly made :class:`State` instance.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state has already been loaded.
        """

        deleted_cls = self.unload_state(
            state_name=state_name, force=force, **kwargs
        )
        self.load_states(deleted_cls, force=force, **kwargs)
        return self.__states[state_name]

    def get_current_state(self) -> Optional[State]:
        """Gets the current State instance.

        Returns
        --------
        Optional[:class:`State`]
            Returns the current State instance.
        """

        return self.__current_state

    def get_last_state(self) -> Optional[State]:
        """Gets the previous State instance.

        Returns
        --------
        Optional[:class:`State`]
            Returns the previous State instance.
        """

        return self.__last_state

    def get_state_map(self) -> Dict[str, State]:
        """Gets the dictionary copy of all states.

        Returns
        --------
        Dict[:class:`str`, :class:`State`]
            Returns the dictionary copy of all states.
        """

        return self.__states.copy()

    def change_state(self, state_name: str) -> None:
        """Changes the current state and updates the last state.

        :param state_name:
            The name of the State you want to switch to.

        Raises
        ------
        :exc:`AssertionError`
            Raised when the state name doesn't exist in the manager.
        """

        assert (
            state_name in self.__states
        ), f"State `{state_name}` isn't present from the available states: "
        f"`{', '.join(self.get_state_map().keys())}`."

        self.__last_state = self.__current_state
        self.__current_state = self.__states[state_name]

    def update_state(self, **kwargs: Any) -> NoReturn:
        r"""Updates the changed State to take place.

        :param \**kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`ExitStateError`
            Raised when the state has successfully exited.

        :exc:`StateError`
            Raised when the current state is `None` i.e having no State to update to.
        """

        if self.__current_state is not None:
            raise ExitStateError(
                "State has successfully exited.",
                last_state=self.__last_state,
                **kwargs,
            )
        raise StateError(
            "No state has been set to exit from.",
            last_state=self.__last_state,
            **kwargs,
        )

    def run_state(self, **kwargs: Any) -> None:
        r"""The entry point to running the StateManager. To be only called once. For
        changing `State`s use `StateManager.change_state` & `StateManager.update_state`

        :param \**kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`StateError`
            Raised when the current state is `None` i.e having no State to run.
        """

        if self.__current_state is not None:
            self.__current_state.run()
        else:
            raise StateError(
                "No state has been set to run.",
                last_state=self.__last_state,
                **kwargs,
            )

    def exit_game(self, **kwargs: Any) -> NoReturn:
        r"""Exits the entire game.

        :param \**kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`ExitStateError`
            Raised when the state has successfully exited.
        """

        raise ExitGameError(
            "Game has successfully exited.",
            last_state=self.__last_state,
            **kwargs,
        )
