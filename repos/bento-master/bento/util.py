from __future__ import unicode_literals

import itertools
import logging
import os
import os.path
import re
import shutil
import signal
import subprocess
import sys
import threading
import types
from functools import partial
from importlib import import_module
from pathlib import Path
from textwrap import wrap as py_wrap
from typing import (
    IO,
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import psutil
import yaml
from click.termui import secho, style
from frozendict import frozendict

import bento.constants as constants

EMPTY_DICT = frozendict({})
MAX_PRINT_WIDTH = 80
MIN_PRINT_WIDTH = 45
ANSI_WIDTH = 4  # number of characters to emit an ANSI control code
LEADER_CHAR = "․"
SETUP_TEXT = "🍜 Setting up"
SETUP_WIDTH = len(SETUP_TEXT)
PROGRESS_TEXT = "🍤 Running".ljust(SETUP_WIDTH, " ")
DONE_TEXT = "🍱 Done".ljust(SETUP_WIDTH, " ")
SKIP_TEXT = "👋 Skipped".ljust(SETUP_WIDTH, " ")
RESET_TEXT = "".ljust(SETUP_WIDTH + 1, "\b")  # +1 for emoji width

OSC_8 = "\x1b]8;;"
BEL = "\x07"

LINK_PRINTER_PATTERN = re.compile("(iterm2|gnome-terminal)", re.IGNORECASE)
LINK_WIDTH = 2 * len(OSC_8) + 2 * len(BEL)

AutocompleteSuggestions = List[Union[str, Tuple[str, str]]]


class Colors:
    LINK = "bright_blue"
    ERROR = "red"
    WARNING = "yellow"
    SUCCESS = "green"


def _calculate_print_width() -> int:
    term_width, _ = shutil.get_terminal_size((MAX_PRINT_WIDTH, 0))
    return max(min(MAX_PRINT_WIDTH, term_width), MIN_PRINT_WIDTH)


PRINT_WIDTH = _calculate_print_width()


def read_global_config() -> Optional[Dict[str, Any]]:
    if not os.path.exists(constants.GLOBAL_CONFIG_PATH):
        return None

    with open(constants.GLOBAL_CONFIG_PATH, "r") as yaml_file:
        try:
            return yaml.safe_load(yaml_file)
        except Exception:
            logging.warning("Invalid global config file found")
            return None


def persist_global_config(global_config: Dict[str, Any]) -> None:
    os.makedirs(constants.GLOBAL_RESOURCE_PATH, exist_ok=True)
    with open(constants.GLOBAL_CONFIG_PATH, "w+") as yaml_file:
        yaml.safe_dump(global_config, yaml_file)

    logging.info(f"Updated user configs at {constants.GLOBAL_CONFIG_PATH}.")


def fetch_line_in_file(path: Path, line_number: int) -> Optional[str]:
    """
    `line_number` is one-indexed! Returns the line if it can be found, returns None if the path doesn't exist
    """
    if not path.exists():
        return None
    with path.open(buffering=1) as fin:  # buffering=1 turns on line-level reads
        return next(itertools.islice(fin, line_number - 1, line_number), None)


def for_name(name: str) -> Type:
    """
    Reflectively obtains a type from a python identifier

    E.g.
        for_name("bento.extra.eslint.EslintTool")
    returns the EslintTool type

    Parameters:
        name (str): The type name, as a python fully qualified identifier
    """
    module_name, class_name = name.rsplit(".", 1)
    mod = import_module(module_name)
    return getattr(mod, class_name)


def is_child_process_of(pattern: Pattern) -> bool:
    """
    Returns true iff this process is a child process of a process whose name matches pattern
    """
    me = psutil.Process()
    parents = me.parents()
    matches = iter(0 for p in parents if pattern.search(p.name()))
    return next(matches, None) is not None


M = TypeVar("M", covariant=True)


class Memo(Generic[M]):
    """
    Creates a (thread-safe) lazily loaded value
    """

    def __init__(self, load: Callable[[], M]) -> None:
        self.load = load
        self._lock = threading.Lock()
        self._value: Optional[M] = None

    @property
    def value(self) -> M:
        with self._lock:
            if self._value is None:
                self._value = self.load()
            return self._value


DO_PRINT_LINKS = is_child_process_of(LINK_PRINTER_PATTERN)


_T = TypeVar("_T")


def batched(it: Iterable[_T], max_len: int) -> Iterator[Iterator[_T]]:
    """
    Batches an iterator in iterators of a maximum length

    :param it: The iterator to batch
    :param max_len: The maximum length
    """
    return (
        (y for _, y in x)
        for _, x in itertools.groupby(enumerate(it), key=lambda x: int(x[0] / max_len))
    )


def less(
    output: Collection[Collection[str]], pager: bool = True, overrun_pages: int = 0
) -> None:
    """
    Possibly prints a string through less.

    Parameters:
        pager: If false, the string is always echoed directly to stdout
        overrun_pages: Minimum number of pages in output before paging is triggered (paging is never triggered if
                       less than or equal to 0)
    """
    use_echo = False
    text = (line for o in output for line in o)
    text_len = sum(len(o) for o in output)

    # In order to prevent an early pager exit from killing the CLI,
    # we must both ignore the resulting SIGPIPE and BrokenPipeError
    def drop_sig(signal: int, frame: Optional[types.FrameType]) -> None:
        pass

    if not pager or not sys.stdout.isatty():
        use_echo = True

    if not use_echo:
        _, height = shutil.get_terminal_size()
        if text_len < height * overrun_pages:
            use_echo = True

    if use_echo:
        for t in text:
            secho(t)
    else:
        # NOTE: Using signal.SIG_IGN here DOES NOT IGNORE the resulting SIGPIPE
        signal.signal(signal.SIGPIPE, drop_sig)
        try:
            process = subprocess.Popen(["less", "-r"], stdin=subprocess.PIPE)
            stdin = cast(IO[bytes], process.stdin)
            for ix, t in enumerate(text):
                stdin.write(bytearray(t, "utf8"))
                if ix != text_len - 1:
                    stdin.write(bytearray("\n", "utf8"))
            process.communicate()
        except BrokenPipeError:
            pass
        finally:
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def wrap(text: str, extra: int = 0) -> str:
    """
    Wraps text to (one character less than) the screen print width

    :param text: The text to wrap
    :param extra: Any extra width to apply
    """
    return "\n".join(py_wrap(text, PRINT_WIDTH - 1 + extra))


def echo_styled(
    text: str, icon: str, log_fn: Callable, fg: str, indent: str = ""
) -> None:
    """
    Print operational messages to stderr with styling.
    Comes with preconfigured functions for common styles:
    `echo_error`, `echo_warning`, and `echo_success`


    :param text: Text to print, will be wrapped line-by-line.
    :param icon: An icon, emoji or otherwise, to prefix the first line with.
    :param log_fn: A function to call with the raw text.
                   Meant to write to log files in the appropriate format.
    :param fg: A click-compatible color name to use as text color.
    :param indent: A string to prepend to every line, such as "  " or "... "

    >>> echo_error("ERROR\nTask failed successfully.", indent="  ")
      ✘ ERROR
      Task failed successfully.
    """
    log_fn(text)
    prefix = f"{icon} "
    lines = text.splitlines()
    for line in lines:
        secho(wrap(f"{indent}{prefix}{line}"), fg=fg, err=True)
        prefix = ""


echo_error = partial(echo_styled, icon="✘", log_fn=logging.error, fg=Colors.ERROR)
echo_warning = partial(echo_styled, icon="⚠", log_fn=logging.warning, fg=Colors.WARNING)
echo_success = partial(echo_styled, icon="✔", log_fn=logging.info, fg=Colors.SUCCESS)


def echo_box(text: str) -> None:
    """
    Prints text bold, in a header box

    By default, the box is PRINT_WIDTH characters wide, unless the text is too
    long for the box, in which case the box is extended to fit.
    """
    lines = text.split("\n")
    max_len = max(len(l) for l in lines)
    max_len = max(PRINT_WIDTH - 4, max_len)
    hrule = "".ljust(max_len + 2, "─")
    echo_newline()
    secho(f"╭{hrule}╮", err=True)
    for l in lines:
        p = style(f"{l:^{max_len}s}", bold=True)
        secho(f"│ {p} │", err=True)
    secho(f"╰{hrule}╯", err=True)


def echo_newline() -> None:
    """
    Prints an informational newline (printed to stderr)
    """
    secho("", err=True)


def echo_styles(*parts: str) -> None:
    """
    Echoes concatenated styled parts to stderr

    :param parts: List of strings to print
    """
    for p in parts:
        if isinstance(p, str):
            secho(p, nl=False, err=True)
    echo_newline()


def echo_next_step(desc: str, cmd: str) -> None:
    """
    Echoes a 'next step' to perform, with styling.

    E.g.

      ◦ To archive results, run $ bento archive

    :param desc: The step description
    :param cmd: The command that the user should run
    """
    echo_styles("◦ ", style(f"{desc}, run $ ", dim=True), cmd)


def echo_progress(text: str, extra: int = 0, skip: bool = False) -> Callable[[], None]:
    """
    Prints a binary in-progress / done bar

    Usage example:
      mark_done = echo_progress("Installing foo")
      install_foo()
      mark_done()

    :param extra: Number of unprinted characters in text (each ANSI code point is 4 characters)
    :param skip: If true, "Skipped" is printed instead, and callback is a no-op
    """
    width = PRINT_WIDTH - 3 - SETUP_WIDTH + ANSI_WIDTH + extra
    logging.info(text)
    leader = style("".ljust(width - len(text), LEADER_CHAR), dim=True)

    if skip:
        secho(f"{text}{leader} {style(SKIP_TEXT, dim=True)}", err=True, dim=True)
        return lambda: None
    else:
        secho(f"{text}{leader} {SETUP_TEXT}", nl=False, err=True, dim=True)
        return lambda: secho(f"{RESET_TEXT}{DONE_TEXT}", err=True, dim=True)


def render_link(
    text: str,
    href: Optional[str],
    print_alternative: bool = True,
    width: Optional[int] = None,
    pipe: TextIO = sys.stdout,
) -> str:
    """
    Prints a clickable hyperlink output if in a tty; otherwise just prints a text link

    :param text: The link anchor text
    :param href: The href, if exists
    :param print_alternative: If true, only emits link if OSC8 links are supported, otherwise prints href after text
    :param width: Minimum link width
    :param pipe: The text IO via which this link will be emitted
    :return: The rendered link
    """
    is_rendered = False
    if href:  # Don't render if href is None or empty
        if pipe.isatty() and DO_PRINT_LINKS:
            text = f"{OSC_8}{href}{BEL}{text}{OSC_8}{BEL}"
            is_rendered = True
            if width:
                width += LINK_WIDTH + len(href)
        elif print_alternative:
            text = f"{text} {href}"

    if width:
        text = text.ljust(width)

    # Coloring has to occur after justification
    if is_rendered:
        text = style(text, fg=Colors.LINK)

    return text


def file_has_text(file: Path, text: str) -> bool:
    """
    Returns if a file contains a pattern
    """
    with file.open() as fd:
        return any(text in l for l in fd)


def append_text_to_file(file: Path, text: str) -> None:
    """
    Adds text to a file
    """
    with file.open("a") as fd:
        fd.write(f"\n{text}\n")
