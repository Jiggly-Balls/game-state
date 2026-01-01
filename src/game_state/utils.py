from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple


__all__ = ("StateArgs", "MISSING", "setup_logging")


@dataclass()
class StateArgs:
    r"""A dataclass to send data to states while loading them in the manager.

    .. versionadded:: 2.1

    :param state_name:
        | The name of the state which the argument belongs to.
    :param kwargs:
        | The data that needs to be sent.
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
        r"""Returns the data to be passed on to the state.
        The data returned does not contain ``state_name`` in it.

        .. versionadded:: 2.1

        :returns:
            | The data of the state arg. Does not include ``state_name`` in it.
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
r"""Used in areas where an attribute doesn't have a value by default but
gets defined during runtime. Lesser type checking would be required by using
this, opposed to using some other default value such as ``None``.

.. versionadded:: 2.0.1
"""

# Below here are the functions / classes for the logging. All of these have been reused
# from the discord.py library with a few modifications. The functions / classes which
# have been reused are: _is_docker, _stream_supports_colour, _ColourFormatter & setup_logging


def _is_docker() -> bool:
    path = "/proc/self/cgroup"
    return os.path.exists("/.dockerenv") or (
        os.path.isfile(path) and any("docker" in line for line in open(path))
    )


def _stream_supports_colour(stream: Any) -> bool:
    is_a_tty = hasattr(stream, "isatty") and stream.isatty()

    # Pycharm and Vscode support colour in their inbuilt editors
    if (
        "PYCHARM_HOSTED" in os.environ
        or os.environ.get("TERM_PROGRAM") == "vscode"
    ):
        return is_a_tty

    if sys.platform != "win32":
        # Docker does not consistently have a tty attached to it
        return is_a_tty or _is_docker()

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    return is_a_tty and ("ANSICON" in os.environ or "WT_SESSION" in os.environ)


class _ColourFormatter(logging.Formatter):
    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS: list[tuple[int, str]] = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS: dict[int, logging.Formatter] = {
        level: logging.Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def setup_logging(
    *,
    handler: Optional[logging.Handler] = None,
    formatter: Optional[logging.Formatter] = None,
    level: Optional[int] = None,
    root: bool = True,
) -> None:
    r"""A helper function to setup logging.

    This is superficially similar to :func:`logging.basicConfig` but
    uses different defaults and a colour formatter if the stream can
    display colour.

    .. versionadded:: 2.4

    :param handler:
        | The log handler to use for the library's logger.
        |
        | The default log handler if not provided is :class:`logging.StreamHandler`.
    :param formatter:
        | The formatter to use with the given log handler.
        | If not provided then it defaults to a colour based logging formatter (if available).
        | If colour is not available then a simple logging formatter is provided.
    :param level:
        | The default log level for the library's logger. Defaults to ``logging.DEBUG``.
    :param root:
        | Whether to set up the root logger rather than the library logger.
    """

    if level is None:
        level = logging.DEBUG

    if handler is None:
        handler = logging.StreamHandler()

    if formatter is None:
        if isinstance(
            handler, logging.StreamHandler
        ) and _stream_supports_colour(handler.stream):  # pyright: ignore[reportUnknownMemberType]
            formatter = _ColourFormatter()
        else:
            formatter = logging.Formatter(
                "[{levelname:^9}] {name}: {message}",
                style="{",
            )

    if root:
        logger = logging.getLogger()
    else:
        library, _, _ = __name__.partition(".")
        logger = logging.getLogger(library)

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)  # pyright: ignore[reportUnknownArgumentType]
