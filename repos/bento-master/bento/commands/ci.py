import sys
from pathlib import Path

import click
import yaml

import bento.content.ci as content
import bento.git
import bento.tool_runner
from bento.context import Context
from bento.decorators import with_metrics
from bento.error import (
    InvalidRegistrationException,
    NotAGitRepoException,
    UnsupportedCIProviderException,
)
from bento.util import echo_next_step, echo_success, echo_warning, read_global_config


def is_ci_configured(context: Context) -> bool:
    return context.gh_actions_file_path.exists()


def is_ci_provider_supported(repo_path: Path) -> bool:
    origin_url = bento.git.url(repo_path)
    if not origin_url:
        return False
    return "github" in origin_url


def _raise_if_unsupported(repo_path: Path) -> None:
    repo = bento.git.repo(repo_path)
    if repo is None:
        raise NotAGitRepoException()

    if not is_ci_provider_supported(repo_path):
        raise UnsupportedCIProviderException()


def _get_user_email() -> str:
    # the Registrar already ran and ensured we have an email
    global_config = read_global_config()
    if global_config is None:  # handling this case only because of mypy
        raise InvalidRegistrationException()
    return global_config["email"]


def _write_gh_actions_config(target_path: Path, email: str) -> None:
    source_path = Path(__file__).parent.parent / "configs" / "gh-actions.yml"

    target_path.parent.mkdir(parents=True, exist_ok=True)

    with source_path.open() as source_file, target_path.open("w") as target_file:
        gh_actions_config = yaml.load(source_file, Loader=yaml.SafeLoader)
        job_config = gh_actions_config["jobs"]["bento"]
        job_config["steps"][-1]["with"]["acceptTermsWithEmail"] = email
        yaml.dump(gh_actions_config, target_file)


def _delete_gh_actions_config(*, path: Path, root_path: Path) -> None:
    """Removes the Bento GitHub Actions config file.

    Also cleans up parent directories recursively if they're left empty.
    """
    path.unlink()

    current_dir = path.parent
    while current_dir != root_path:
        try:
            current_dir.rmdir()
        except OSError:
            return  # directory not empty, cleanup done
        current_dir = current_dir.parent


@click.command(name="ci")
@click.pass_obj
@with_metrics
def install_ci(context: Context) -> None:
    """
    Configures Bento to run in CI.
    """
    _raise_if_unsupported(context.base_path)

    pretty_path = context.pretty_path(context.gh_actions_file_path)
    config_directory = pretty_path.parts[0]

    if not context.is_init:
        # confirmation was handled as part of init
        content.Install.banner.echo()

        if is_ci_configured(context):
            content.Overwrite.warn.echo(str(pretty_path).strip())

            is_overwrite_confirmed = content.Overwrite.confirm.echo()
            content.Overwrite.after_confirm.echo()
            if not is_overwrite_confirmed:
                sys.exit()

        on_done = content.Install.progress.echo(config_directory)

    _write_gh_actions_config(context.gh_actions_file_path, _get_user_email())

    if not context.is_init:
        on_done()

        content.Install.after_progress.echo()
        content.Install.finalize_ci.echo()


@click.command(name="ci")
@click.pass_obj
@with_metrics
def uninstall_ci(context: Context) -> None:
    """
    Configures Bento to NOT run in CI.
    """
    repo = bento.git.repo(context.base_path)
    if repo is None:
        raise NotAGitRepoException()

    if not context.gh_actions_file_path.exists():
        echo_warning(
            "Not uninstalling CI config: Bento is not configured for CI on this project."
        )
        sys.exit(1)

    _delete_gh_actions_config(
        path=context.gh_actions_file_path, root_path=context.base_path
    )

    echo_success("Uninstalled Bento from CI.")
    echo_next_step("To re-enable CI integration", "bento enable ci")
