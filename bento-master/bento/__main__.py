#!/usr/bin/env python3
import sys

from bento.cli import cli
from bento.error import BentoException
from bento.util import echo_error


def main() -> None:
    try:
        cli(auto_envvar_prefix="BENTO")
    # Catch custom exceptions, output the right message and exit.
    # Note: this doesn't catch all Exceptions and lets them bubble up.
    except BentoException as e:
        if e.msg:
            echo_error(e.msg)
        sys.exit(3)


if __name__ == "__main__":
    main()
