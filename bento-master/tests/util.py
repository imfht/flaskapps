import contextlib
import re
import subprocess
from pathlib import Path
from typing import Iterator, TextIO

ANSI_CONTROL = "\x1b\\["
ANSI_SUB_SEQ = re.compile(
    ANSI_CONTROL + r"(\d+[ABCDEFGJKSTm]|\d+;\d+[fH]|5i|4i|6n|s|u)"
)


@contextlib.contextmanager
def mod_file(path: Path) -> Iterator[TextIO]:
    """
    Opens a path for read, then reverts it.
    """
    try:
        with path.open() as file:
            yield file
    finally:
        subprocess.run(["git", "checkout", str(path)], check=True)


def strip_ansi(text: str) -> str:
    """
    Removes ANSI control characters from a string
    """
    return ANSI_SUB_SEQ.sub("", text)
