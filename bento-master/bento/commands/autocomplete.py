import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Tuple

import click

from bento.decorators import with_metrics
from bento.util import append_text_to_file, echo_error, echo_success, file_has_text

ZSH_TEXT = 'eval "$(_BENTO_COMPLETE=source_zsh bento)"'
BASH_TEXT = 'eval "$(_BENTO_COMPLETE=source bento)"'

SUPPORTED = {"bash": (".bashrc", BASH_TEXT), "zsh": (".zshrc", ZSH_TEXT)}
VALID = ",".join(SUPPORTED.keys())


def _validate_shell() -> Tuple[Path, str]:
    """
    Gets the profile file and completion text for the current shell

    :raises SystemExit: If not in a valid shell
    """
    shell_env = os.environ.get("SHELL")
    logging.info(f"Using shell {shell_env}")
    if not shell_env:
        echo_error(
            f"This command must be executed within one of the {VALID} shells. (Currently not in a shell)."
        )
        sys.exit(1)

    shell = shell_env.split("/")[-1]
    if shell not in SUPPORTED:
        echo_error(
            f"This command must be executed within one of the {VALID} shells. (Currently using {shell})."
        )
        sys.exit(1)

    profile, text = SUPPORTED[shell]
    path = Path.home() / profile

    return path, text


@click.command(name="autocomplete")
@with_metrics
def install_autocomplete(quiet: bool = False) -> None:
    """
    Enable tab autocompletion in your shell profile.
    """
    path, text = _validate_shell()

    if not path.exists():
        path.touch(mode=0o644)

    if not file_has_text(path, text):
        append_text_to_file(path, text)

    if not quiet:
        echo_success(
            f"Tab autocompletion for Bento has been added to {path}. Please run `source {path}`."
        )


@click.command(name="autocomplete")
@with_metrics
def uninstall_autocomplete() -> None:
    """
    Remove tab autocompletion from your shell profile.
    """
    path, text = _validate_shell()

    # Removes "{text}\n" from file; however, it leaves the preceding newline.
    # This is simply because the logic got complicated otherwise.

    omit_next_newline = False
    swap_fd, swap_path = tempfile.mkstemp(prefix="path_", text=True)
    try:
        with path.open() as profile_fd:
            for line in profile_fd:
                if line.strip() == text:
                    omit_next_newline = True
                elif omit_next_newline and line == "\n":
                    omit_next_newline = False
                else:
                    omit_next_newline = False
                    os.write(swap_fd, line.encode())
        os.fsync(swap_fd)
        shutil.copyfile(swap_path, path)
    finally:
        os.close(swap_fd)
        os.remove(swap_path)

    echo_success(f"Tab autocompletion for Bento has been removed from {path}.")
