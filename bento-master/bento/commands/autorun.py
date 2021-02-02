import os
import shutil
import stat
import sys
from pathlib import Path

import click

import bento.constants as constants
import bento.git
import bento.tool_runner
from bento.context import Context
from bento.decorators import with_metrics
from bento.error import ExistingGitHookException, NotAGitRepoException
from bento.util import echo_next_step, echo_success, echo_warning


def _is_bento_precommit(filename: Path) -> bool:
    if not filename.exists():
        return False
    with filename.open() as lines:
        return any(constants.BENTO_TEMPLATE_HASH in l for l in lines)


def _configure_block(context: Context, block: bool) -> None:
    config = context.config
    autorun_config = config.get(constants.AUTORUN, {})
    autorun_config[constants.AUTORUN_BLOCK] = block
    config[constants.AUTORUN] = autorun_config
    context.config = config


def _notify_install(context: Context, block: bool) -> None:
    if not context.is_init:
        block_prefix = "" if block else "non-"
        echo_success(f"Installed Bento autorun in {block_prefix}blocking mode.")
        echo_next_step("To uninstall Bento autorun", "bento disable autorun")

        desc_prefix, cmd_prefix = ("", "") if not block else ("non-", "no-")
        echo_next_step(
            f"To make autorun {desc_prefix}blocking",
            f"bento enable autorun --{cmd_prefix}block",
        )


@click.command(name="autorun")
@click.option(
    "--block/--no-block",
    default=True,
    help="If --block, commits will fail if Bento finds an issue.",
)
@click.pass_obj
@with_metrics
def install_autorun(context: Context, block: bool) -> None:
    """
    Configures Bento to automatically run on commits.

    Autorun is configured only for you; it does not affect
    other contributors to this project.

    Autorun is only configured for the project from which this
    command is run.

    By default, Bento will block commits if it finds an issue.
    To prevent autorun from blocking commits, run:

        $ bento enable autorun --no-block

    """
    import git  # import inside def for performance

    # Get hook path
    repo = bento.git.repo(context.base_path)
    if repo is None:
        raise NotAGitRepoException()

    _configure_block(context, block)

    hook_path = Path(git.index.fun.hook_path("pre-commit", repo.git_dir))

    if _is_bento_precommit(hook_path):
        _notify_install(context, block)

    else:
        legacy_hook_path = Path(f"{hook_path}.pre-bento")
        if hook_path.exists():
            # If pre-commit hook already exists move it over
            if legacy_hook_path.exists():
                raise ExistingGitHookException(str(hook_path))
            else:
                # Check that
                shutil.move(str(hook_path), str(legacy_hook_path))

        # Ensure .git/hooks directory exists
        # note that we can (and should) assume .git dir exists since
        # project must be a git project at this point in the code
        hook_path.parent.mkdir(exist_ok=True)

        # Copy pre-commit script template to hook_path
        template_location = os.path.join(
            os.path.dirname(__file__), "../configs/pre-commit.template"
        )
        shutil.copyfile(template_location, hook_path)

        # Make file executable
        original_mode = hook_path.stat().st_mode
        os.chmod(hook_path, original_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        _notify_install(context, block)


@click.command(name="autorun")
@click.pass_obj
@with_metrics
def uninstall_autorun(context: Context) -> None:
    """
    Configures Bento to NOT run automatically on commits.

    Autorun is only removed for the project from which this
    command is run.
    """
    import git  # import inside def for performance

    # Get hook path
    repo = bento.git.repo(context.base_path)
    if repo is None:
        raise NotAGitRepoException()

    hook_path = Path(git.index.fun.hook_path("pre-commit", repo.git_dir))

    if not _is_bento_precommit(hook_path):
        echo_warning(
            "Not uninstalling autorun: Bento is not configured for autorun on this project."
        )
        sys.exit(1)
    else:
        # Put back legacy hook if exits
        legacy_hook_path = Path(f"{hook_path}.pre-bento")
        if legacy_hook_path.exists():
            shutil.move(str(legacy_hook_path), str(hook_path))
        else:
            hook_path.unlink()

        echo_success("Uninstalled Bento autorun.")
        echo_next_step("To enable autorun", "bento enable autorun")
