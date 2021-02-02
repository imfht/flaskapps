import logging
import time
from typing import Collection, Iterable, Tuple

import click

from bento.constants import IGNORE_FILE_NAME
from bento.result import Baseline
from bento.target_file_manager import NoGitHeadException, TargetFileManager
from bento.tool import Tool
from bento.tool_runner import Runner, RunResults, RunStep
from bento.util import echo_warning


# TODO baseline removal should not be part of tool running
def orchestrate(
    baseline: Baseline,
    target_file_manager: TargetFileManager,
    staged: bool,
    tools: Iterable[Tool],
) -> Tuple[Collection[RunResults], float]:
    """
        Manages interactions between TargetFileManager, Runner and Tools

        Uses passed target_file_manager, staged flag, and tool list to setup
        Runner and runs tools on relevant files, returning aggregated output
        of tool running and time to run all tools in parallel
    """
    elapsed = 0.0
    if staged:
        head_baseline, elapsed = _calculate_head_comparison(target_file_manager, tools)
        for t in tools:
            tool_id = t.tool_id()
            if tool_id not in baseline:
                baseline[tool_id] = head_baseline.get(tool_id, set())
            else:
                baseline[tool_id].update(head_baseline.get(tool_id, set()))

    with target_file_manager.run_context(staged, RunStep.CHECK) as target_paths:
        use_cache = not staged  # if --all then can use cache
        skip_setup = staged  # if check --all then include setup
        runner = Runner(paths=target_paths, use_cache=use_cache, skip_setup=skip_setup)

        if len(runner.paths) == 0:
            echo_warning(
                f"Nothing to check or archive. Please confirm that changes are staged and not excluded by `{IGNORE_FILE_NAME}`. To check all Git tracked files, use `--all`."
            )
            click.secho("", err=True)
            all_results: Collection[RunResults] = []
            elapsed = 0.0
        else:
            before = time.time()
            all_results = runner.parallel_results(tools, baseline)
            elapsed += time.time() - before

    return all_results, elapsed


def _calculate_head_comparison(
    target_file_manager: TargetFileManager, tools: Iterable[Tool]
) -> Tuple[Baseline, float]:
    """
    Calculates a baseline consisting of all findings from the branch head

    If no HEAD branch exists return empty baseline

    :param paths: Which paths are being checked
    :param tools: Which tools to check
    :return: The branch head baseline
    """
    try:
        with target_file_manager.run_context(True, RunStep.BASELINE) as target_paths:
            runner = Runner(paths=target_paths, use_cache=True, skip_setup=True)
            if len(runner.paths) > 0:
                before = time.time()
                comparison_results = runner.parallel_results(tools, {}, keep_bars=False)
                baseline = {
                    tool_id: {f.syntactic_identifier_str() for f in findings}
                    for tool_id, findings in comparison_results
                    if isinstance(findings, list)
                }
                elapsed = time.time() - before
                return baseline, elapsed
            else:
                return {}, 0.0
    except NoGitHeadException:
        logging.debug("No git head found so defaulting to empty head baseline")
        return {}, 0.0
