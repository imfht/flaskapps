import logging
import os
import sys
import time
from distutils.util import strtobool
from pathlib import Path
from typing import Optional

import click
from packaging.version import InvalidVersion, Version

import bento.constants as constants
import bento.network
from bento.commands import archive, check, disable, enable, init, register
from bento.context import Context
from bento.error import InvalidRegistrationException, OutdatedPythonException


def _setup_logging() -> None:
    os.makedirs(os.path.dirname(constants.DEFAULT_LOG_PATH), exist_ok=True)
    logging.basicConfig(
        filename=constants.DEFAULT_LOG_PATH,
        level=logging.DEBUG,
        filemode="w",
        format="[%(levelname)s] %(relativeCreated)s %(name)s:%(module)s - %(message)s",
    )
    logging.info(
        f"Environment: stdout.isatty={sys.stdout.isatty()} stderr.isatty={sys.stderr.isatty()} stdin.isatty={sys.stdin.isatty()}"
    )
    # Very noisy logging from urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _is_test() -> bool:
    test_var = os.getenv(constants.BENTO_TEST_VAR, "0")
    try:
        return strtobool(test_var) == 1
    except ValueError:
        return False


def _get_version_from_cache(version_cache_path: Path) -> Optional[Version]:
    """
        Reads version cache file and returns Version stored in it
        if time cache was written was within the last day.

        Returns None if version cache is invalid for any reason
        or file does not exist
    """
    now = time.time()
    if version_cache_path.is_file():
        with version_cache_path.open() as f:
            timestamp_str = f.readline().strip()
            latest_version_str = f.readline().strip()
            try:
                latest_version = Version(latest_version_str)
            except InvalidVersion:
                logging.debug(
                    f"Version Cache invalid version string: {latest_version_str}"
                )
                return None

            try:
                # Treat time as integer seconds so no need to deal with str float conversion
                timestamp = int(timestamp_str)
            except ValueError:
                logging.debug(f"Version Cache invalid timestamp: {timestamp_str}")
                return None

            if now - timestamp > 86400:
                logging.debug(f"Version Cache expired {timestamp}:{now}")
                return None

            logging.debug(f"Version Cache returning {latest_version}")
            return latest_version
    logging.debug("Version Cache does not exist")
    return None


def _get_latest_version(version_cache_path: Path) -> Optional[Version]:
    """
        Return latest Version of bento-cli available.

        Checks local version cache to save from making network call
        but if cache is invalid makes network call and writes to cache.

        Returns None if cache is invalid and network call fails for
        any reason
    """
    latest_version = _get_version_from_cache(version_cache_path)
    if latest_version is None:
        latest_version_str, _ = bento.network.fetch_latest_version()
        if latest_version_str is None:
            # Request timed out or invalid
            return None

        try:
            latest_version = Version(latest_version_str)
        except InvalidVersion:
            # latest version str from server incorrect
            return None

        # Write to version cache
        with version_cache_path.open("w") as f:
            # Integer time so no need to deal with str float conversions
            f.write(f"{int(time.time())}\n")
            f.write(latest_version_str)

    return latest_version


def _is_running_latest() -> bool:
    """
        Returns True if current version of bento is latest version available
    """
    latest_version = _get_latest_version(constants.GLOBAL_VERSION_CACHE_PATH)
    current_version = Version(_get_version())
    logging.info(
        f"Current bento version is {current_version}, latest is {latest_version}"
    )
    if latest_version and current_version < latest_version:
        return False
    return True


def _get_version() -> str:
    """Get the current r2c-cli version based on __init__"""
    from bento import __version__

    return __version__


def _is_running_supported_python3() -> bool:
    python_major_v = sys.version_info.major
    python_minor_v = sys.version_info.minor
    logging.info(f"Python version is ({python_major_v}.{python_minor_v})")
    return python_major_v >= 3 and python_minor_v >= 6


@click.group(epilog="To get help for a specific command, run `bento COMMAND --help`")
@click.help_option("-h", "--help")
@click.version_option(
    prog_name="bento", version=_get_version(), message="%(prog)s/%(version)s"
)
@click.option(
    "--base-path",
    help=f"Path to the project to run bento in.",
    type=click.Path(exists=True, file_okay=False),
    default=None,
    hidden=True,
)
@click.option(
    "--agree",
    is_flag=True,
    help="Automatically agree to terms of service.",
    default=False,
)
@click.option(
    "--email",
    type=str,
    help="Email address to use while running this command without global configs e.g. in CI",
    default=None,
)
@click.pass_context
def cli(
    ctx: click.Context, base_path: Optional[str], agree: bool, email: Optional[str]
) -> None:
    _setup_logging()
    is_init = ctx.invoked_subcommand == "init"
    ctx.help_option_names = ["-h", "--help"]
    if base_path is None:
        ctx.obj = Context(is_init=is_init, email=email)
    else:
        ctx.obj = Context(base_path=base_path, is_init=is_init, email=email)
    if not _is_running_supported_python3():
        raise OutdatedPythonException()

    registrar = register.Registrar(ctx, agree, email=email)
    if not registrar.verify():
        raise InvalidRegistrationException()

    if not _is_running_latest() and not _is_test():
        logging.warning("Bento client is outdated")
        click.secho(constants.UPGRADE_WARNING_OUTPUT, err=True)


cli.add_command(archive.archive)
cli.add_command(check.check)
cli.add_command(init.init)
cli.add_command(enable.enable)
cli.add_command(disable.disable)
