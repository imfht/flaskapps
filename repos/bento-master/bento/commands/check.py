import logging
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import click

import bento.constants
import bento.formatter
import bento.metrics
import bento.network
import bento.orchestrator
import bento.result
import bento.tool_runner
from bento.config import get_valid_tools, update_tool_run
from bento.context import Context
from bento.decorators import with_metrics
from bento.error import (
    BentoException,
    NoConfigurationException,
    NodeError,
    NoIgnoreFileException,
    ToolRunException,
)
from bento.paths import list_paths
from bento.result import Baseline
from bento.target_file_manager import TargetFileManager
from bento.tool import Tool
from bento.util import echo_error, echo_next_step, echo_success, echo_warning
from bento.violation import Violation

OVERRUN_PAGES = 3


def __get_ignores_for_tool(tool: str, config: Dict[str, Any]) -> List[str]:
    tool_config = config["tools"]
    tool_specific_config = tool_config[tool] or {}
    return tool_specific_config.get("ignore", [])


@click.command()
@click.option(
    "--all",
    "all_",
    is_flag=True,
    default=False,
    help="Show unarchived findings for all tracked files.",
)
@click.option(
    "-f",
    "--formatter",
    type=click.Choice(bento.formatter.FORMATTERS.keys()),
    help=f"Which output format to use. Falls back to the formatter(s) configured in `{bento.constants.CONFIG_FILE_NAME}`.",
    multiple=True,
)
@click.option(
    "--pager/--no-pager",
    help="Send long output through a pager. This should be disabled when used as an integration (e.g. with an editor).",
    default=True,
)
@click.option(
    "-t",
    "--tool",
    help="Specify a previously configured tool to run.",
    metavar="TOOL",
    autocompletion=get_valid_tools,
)
@click.option("--staged-only", is_flag=True, default=False, hidden=True)
@click.argument("paths", nargs=-1, type=Path, autocompletion=list_paths)
@click.pass_obj
@with_metrics
def check(
    context: Context,
    all_: bool = False,
    formatter: Tuple[str, ...] = (),
    pager: bool = True,
    tool: Optional[str] = None,
    staged_only: bool = False,  # Should not be used. Legacy support for old pre-commit hooks
    paths: Tuple[Path, ...] = (),
) -> None:
    """
    Checks for new findings.

    By default, only staged files are checked. New findings introduced by
    these staged changes AND that are not in the archive (`.bento/archive.json`)
    will be shown.

    Use `--all` to check all Git tracked files, not just those that are staged:

        $ bento check --all [PATHS]

    Optional PATHS can be specified to check specific directories or files.

    See `bento archive --help` to learn about suppressing findings.
    """

    # Fail out if not configured
    if not context.config_path.exists():
        raise NoConfigurationException()

    # Fail out if no .bentoignore
    if not context.ignore_file_path.exists():
        raise NoIgnoreFileException(context)

    # Default to no path filter
    if len(paths) < 1:
        path_list = [context.base_path]
    else:
        path_list = list(paths)

    # Handle specified tool that is not configured
    if tool and tool not in context.configured_tools:
        click.echo(
            f"{tool} has not been configured. Adding default configuration for tool to {bento.constants.CONFIG_FILE_NAME}"
        )
        update_tool_run(context, tool, False)
        # Set configured_tools to None so that future calls will
        # update and include newly added tool
        context._configured_tools = None

    # Handle specified formatters
    if formatter:
        context.config["formatter"] = [{f: {}} for f in formatter]

    if all_:
        click.echo(f"Running Bento checks on all tracked files...\n", err=True)
    else:
        click.echo(f"Running Bento checks on staged files...\n", err=True)

    tools: Iterable[Tool[Any]] = context.tools.values()
    if tool:
        tools = [context.configured_tools[tool]]

    baseline: Baseline = {}
    if context.baseline_file_path.exists():
        with context.baseline_file_path.open() as json_file:
            baseline = bento.result.json_to_violation_hashes(json_file)

    target_file_manager = TargetFileManager(
        context.base_path, path_list, not all_, context.ignore_file_path
    )

    all_results, elapsed = bento.orchestrator.orchestrate(
        baseline, target_file_manager, not all_, tools
    )

    fmts = context.formatters
    findings_to_log: List[Any] = []
    n_all = 0
    n_all_filtered = 0
    filtered_findings: Dict[str, List[Violation]] = {}
    for tool_id, findings in all_results:
        if isinstance(findings, Exception):
            logging.error(findings)
            echo_error(f"Error while running {tool_id}: {findings}")
            if isinstance(findings, BentoException):
                click.secho(findings.msg, err=True)
            else:
                if isinstance(findings, subprocess.CalledProcessError):
                    click.secho(findings.stderr, err=True)
                    click.secho(findings.stdout, err=True)
                if isinstance(findings, NodeError):
                    echo_warning(
                        f"Node.js not found or version is not compatible with ESLint v6."
                    )
                click.secho(
                    f"""-------------------------------------------------------------------------------------------------
    This may be due to a corrupted tool installation. You might be able to fix this issue by running:

    bento init --clean

    You can also view full details of this error in `{bento.constants.DEFAULT_LOG_PATH}`.
    -------------------------------------------------------------------------------------------------
    """,
                    err=True,
                )
            context.error_on_exit(ToolRunException())
        elif isinstance(findings, list) and findings:
            findings_to_log += bento.metrics.violations_to_metrics(
                tool_id,
                context.timestamp,
                findings,
                __get_ignores_for_tool(tool_id, context.config),
            )
            filtered = [f for f in findings if not f.filtered]
            filtered_findings[tool_id] = filtered

            n_all += len(findings)
            n_filtered = len(filtered)
            n_all_filtered += n_filtered
            logging.debug(f"{tool_id}: {n_filtered} findings passed filter")

    def post_metrics() -> None:
        bento.network.post_metrics(findings_to_log, is_finding=True)

    stats_thread = threading.Thread(name="stats", target=post_metrics)
    stats_thread.start()

    dumped = [f.dump(filtered_findings) for f in fmts]
    context.start_user_timer()
    bento.util.less(dumped, pager=pager, overrun_pages=OVERRUN_PAGES)
    context.stop_user_timer()

    finding_source_text = "in this project" if all_ else "due to staged changes"
    if n_all_filtered > 0:
        echo_warning(
            f"{n_all_filtered} finding(s) {finding_source_text} in {elapsed:.2f} s"
        )
        click.secho("\nPlease fix these issues, or:\n", err=True)
        echo_next_step("To archive findings as tech debt", f"bento archive")
        echo_next_step("To disable a specific check", f"bento disable check TOOL CHECK")
    else:
        echo_success(f"0 findings {finding_source_text} in {elapsed:.2f} s\n")

    n_archived = n_all - n_all_filtered
    if n_archived > 0:
        echo_next_step(
            f"Not showing {n_archived} archived finding(s). To view",
            "cat .bento/archive.json",
        )

    if not all_ and not context.autorun_is_blocking:
        return
    elif context.on_exit_exception:
        raise context.on_exit_exception
    elif n_all_filtered > 0:
        sys.exit(2)
