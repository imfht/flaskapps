import logging
import subprocess
import time
from datetime import datetime
from functools import update_wrapper
from typing import Any, Callable, List, Optional

import click

import bento.metrics
import bento.network
from bento.error import BentoException
from bento.util import echo_error, echo_warning

_AnyCallable = Callable[..., Any]


def __log_exception(e: Exception) -> None:
    logging.exception(e)
    if isinstance(e, subprocess.CalledProcessError):
        cmd = e.cmd
        if isinstance(e.cmd, list):
            cmd = " ".join([str(part) for part in e.cmd])
        echo_warning(f'Could not execute "{cmd}":\n{e.stderr}')
        logging.error(e.stdout)
        logging.error(e.stderr)
    else:
        echo_error(f"There was an exception {e}")


def with_metrics(f: _AnyCallable) -> _AnyCallable:
    def new_func(*args: Any, **kwargs: Any) -> Any:
        exit_code = 0
        before = time.time()

        context = click.get_current_context()

        commands: List[str] = [context.command.name]
        current_context = context
        while current_context.parent:
            current_context = current_context.parent

            # Don't include "cli" in the command string. This is a quirk in click command nesting
            if current_context.command.name != "cli":
                commands.insert(0, current_context.command.name)

        command_str: str = " ".join(commands)

        logging.info(f"command: {command_str}")

        cli_context = context.obj
        timestamp = (
            cli_context.timestamp if cli_context else datetime.utcnow().isoformat("T")
        )
        logging.info(f"Executing {command_str}")

        exception: Optional[BaseException] = None
        try:
            res = f(*args, **kwargs)
        except KeyboardInterrupt as e:
            # KeyboardInterrupt is a BaseException and has no exit code. Use 130 to mimic bash behavior.
            exit_code = 130
            exception = e
        except BentoException as e:
            exit_code = e.code
            exception = e
        except SystemExit as e:
            exit_code = e.code
            exception = e
        except Exception as e:
            exit_code = 3
            __log_exception(e)
            exception = e

        exc_name = exception.__class__.__name__ if exception else None

        elapsed = time.time() - before
        user_duration = cli_context.user_duration() if cli_context else None

        if exc_name == "KeyboardInterrupt":
            logging.info(f"{command_str} interrupted after running for {elapsed}s")
        else:
            logging.info(
                f"{command_str} completed in {elapsed}s with exit code {exit_code}"
            )

        email = (
            cli_context.email
            if cli_context and cli_context.email
            else bento.metrics.read_user_email()
        )

        logging.info(
            f"______________exit code: {exit_code}, exception name: {exc_name}_______________"
        )

        bento.network.post_metrics(
            bento.metrics.command_metric(
                command_str,
                email,
                timestamp,
                kwargs,
                exit_code,
                elapsed,
                exc_name,
                user_duration,
            )
        )
        if exception:
            raise exception
        return res

    return update_wrapper(new_func, f)
