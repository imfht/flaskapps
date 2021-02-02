import logging
import multiprocessing.synchronize
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from enum import Enum
from functools import partial
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Collection, Iterable, Iterator, List, Optional, Tuple, Union

import attr
import click
from tqdm import tqdm

import bento.result
import bento.util
from bento.error import NoToolsConfiguredException
from bento.result import Baseline
from bento.tool import Tool
from bento.violation import Violation

DONE_BAR_VALUE = 30
BAR_UPDATE_INTERVAL = 0.1

SLOW_RUN_SECONDS = 60  # Number of seconds before which a "slow run" warning is printed

ToolResults = Union[List[Violation], Exception]
RunResults = Tuple[str, ToolResults]

START_RUN_BAR_VALUE = int(DONE_BAR_VALUE / 5)


class RunStep(Enum):
    BASELINE = 1
    CHECK = 2


@attr.s
class Runner:
    paths = attr.ib(type=List[Path])
    use_cache = attr.ib(type=bool)
    skip_setup = attr.ib(type=bool, default=False)
    show_bars = attr.ib(type=bool, default=True)
    install_only = attr.ib(type=bool, default=False)
    _lock = attr.ib(type=multiprocessing.synchronize.Lock, factory=Lock, init=False)
    _bars = attr.ib(type=List[tqdm], factory=list, init=False)
    _run = attr.ib(type=List[bool], factory=list, init=False)
    _done = attr.ib(type=bool, default=False, init=False)

    def __attrs_post_init__(self) -> None:
        self.show_bars = self.show_bars and sys.stderr.isatty()

    def _update_bars(self, ix: int, lower: int, upper: int) -> None:
        """
        Increments a progress bar
        """
        bar_value = lower
        keep_going = True
        bar = self._bars[ix]
        while keep_going:
            with self._lock:
                keep_going = self._run[ix]
                if bar_value < upper - 1:
                    bar_value += 1
                    bar.update(1)
                else:
                    bar_value = lower
                    bar.update(lower - upper + 1)
            time.sleep(BAR_UPDATE_INTERVAL)
        with self._lock:
            bar.update(upper - bar_value)

    def _setup_bars(self, indices_and_tools: List[Tuple[int, Tool]]) -> None:
        """
        Constructs progress bars for all tools
        """
        self._bars = [
            tqdm(
                total=DONE_BAR_VALUE,
                position=ix,
                ascii="□■",
                mininterval=BAR_UPDATE_INTERVAL,
                desc=tool.tool_id().ljust(
                    bento.util.PRINT_WIDTH - 34, bento.util.LEADER_CHAR
                ),
                ncols=bento.util.PRINT_WIDTH - 2,
                bar_format=click.style("{desc:s}|{bar}| {elapsed}{postfix}", dim=True),
                leave=False,
            )
            for ix, tool in indices_and_tools
        ]

    @contextmanager
    def _updating_bar(
        self,
        bar: Optional[tqdm],
        ix: int,
        min_value: int,
        max_value: int,
        start_text: str,
        done_text: str,
    ) -> Iterator[None]:
        """
        Runs a block with an updating progress bar

        :param bar: The progress bar (or None if no progress bar is displayed for this item)
        :param ix: The progress bar index
        :param min_value: Min value to display
        :param max_value: Max value to display
        """
        th: Optional[threading.Thread] = None
        self._run[ix] = True
        if bar:
            with self._lock:
                bar.set_postfix_str(start_text)
            th = threading.Thread(
                name=f"update_{ix}",
                target=partial(self._update_bars, ix, min_value, max_value),
            )
            th.start()
        try:
            yield
        finally:
            self._run[ix] = False
            if th:
                th.join()
            if bar:
                with self._lock:
                    bar.n = max_value
                    bar.update(0)
                    bar.set_postfix_str(done_text)

    def _echo_slow_run(self) -> None:
        """
        Echoes a warning to the screen that Bento is taking longer than expected.

        Wipes and resets any progress bars.
        """
        before = time.monotonic()

        while not self._done and time.monotonic() - before < SLOW_RUN_SECONDS:
            time.sleep(BAR_UPDATE_INTERVAL)

        if not self._done:
            with self._lock:
                if self.show_bars:
                    wipe_line = "".ljust(bento.util.PRINT_WIDTH, " ")

                    click.echo(
                        "\x1b[0G", nl=False, err=True
                    )  # Reset cursor to beginning of line
                    click.echo("\x1b[s", nl=False, err=True)  # Save cursor state
                    for _ in range(len(self._bars) - 1):
                        click.echo(wipe_line, err=True)
                    # Handling last line separately prevents screen roll
                    click.echo(wipe_line, nl=False, err=True)
                    click.echo("\x1b[u", nl=False, err=True)  # Retrieve cursor state

                click.secho(
                    bento.util.wrap(
                        f"Bento is taking longer than expected, which may mean it’s checking build or dependency "
                        f"code. This is often unintentional or unexpected.",
                        extra=-4,
                    )
                    + "\n\n"
                    + bento.util.wrap(
                        "Please make sure all build and dependency "
                        f"files are included in your `.bentoignore`, or try running Bento on specific files via `bento "
                        f"check [PATH]`",
                        extra=-4,
                    ),
                    err=True,
                    fg=bento.util.Colors.WARNING,
                    bold=False,
                )
                bento.util.echo_newline()
        else:
            logging.debug(f"Bento run completed in less than {SLOW_RUN_SECONDS} s.")

    def _setup_tool(
        self,
        bar: Optional[tqdm],
        ix: int,
        tool: Tool,
        max_bar_value: int,
        end_text: str,
    ) -> None:
        """
        Ensures that a tool is installed.

        :param bar: Any associated progress bar
        :param ix: The bar index
        :param tool: The tool
        """
        with self._updating_bar(
            bar, ix, 0, max_bar_value, bento.util.SETUP_TEXT, end_text
        ):
            tool.setup()

    def _run_single_tool(
        self, bar: Optional[tqdm], ix: int, tool: Tool, baseline: Baseline
    ) -> ToolResults:
        """
        Returns results for running a previously installed tool.

        :param bar: The progress bar associated with this tool
        :param ix: The current tool index
        :param tool: The tool itself
        :param paths: Paths to pass to the tool
        :param baseline: Any baseline to subtract from this tool
        :return: Tool results
        """
        with self._updating_bar(
            bar,
            ix,
            START_RUN_BAR_VALUE,
            DONE_BAR_VALUE,
            bento.util.PROGRESS_TEXT,
            bento.util.DONE_TEXT,
        ):
            results = bento.result.filtered(
                tool.tool_id(), tool.results(self.paths, self.use_cache), baseline
            )

        return results

    def _setup_and_run_single_tool(
        self, baseline: Baseline, index_and_tool: Tuple[int, Tool]
    ) -> RunResults:
        """Runs a tool and filters out existing findings using baseline"""

        ix, tool = index_and_tool
        end_of_setup_bar_value = (
            DONE_BAR_VALUE if self.install_only else START_RUN_BAR_VALUE
        )
        end_of_setup_text = (
            bento.util.DONE_TEXT if self.install_only else bento.util.PROGRESS_TEXT
        )
        bar = self._bars[ix] if self.show_bars else None

        try:
            before = time.time()
            logging.debug(f"{tool.tool_id()} start")

            if not self.skip_setup:
                self._setup_tool(
                    bar, ix, tool, end_of_setup_bar_value, end_of_setup_text
                )
            after_setup = time.time()

            results: ToolResults = []
            if not self.install_only:
                results = self._run_single_tool(bar, ix, tool, baseline)

            after = time.time()
            logging.debug(
                f"{tool.tool_id()} completed in {(after - before):2f} s (setup in {(after_setup - before):2f} s)"
            )

            return tool.tool_id(), results
        except Exception as e:
            logging.error(traceback.format_exc())
            return tool.tool_id(), e

    def parallel_results(
        self, tools: Iterable[Tool], baseline: Baseline, keep_bars: bool = True
    ) -> Collection[RunResults]:
        """Runs all tools in parallel.

        Each tool is optionally run against a list of files. For each tool, it's results are
        filtered to those results not appearing in the whitelist.

        A progress bar is emitted to stderr for each tool.

        Parameters:
            tools: (iterable): Tools to run
            baseline (set): The set of whitelisted finding hashes
            keep_bars (bool): If true, progress bars are preserved after run (default True)

        Returns:
            (collection): For each tool, a `RunResult`, which is a tuple of (`tool_id`, `findings`)
        """
        indices_and_tools = list(enumerate(tools))
        n_tools = len(indices_and_tools)

        if n_tools == 0:
            raise NoToolsConfiguredException()

        if self.show_bars:
            self._setup_bars(indices_and_tools)
        self._run = [True for _, _ in indices_and_tools]
        self._done = False

        slow_run_thread = threading.Thread(
            name="slow_run_timer", target=self._echo_slow_run
        )
        slow_run_thread.start()

        with ThreadPool(n_tools) as pool:
            # using partial to pass in multiple arguments to __tool_filter
            func = partial(Runner._setup_and_run_single_tool, self, baseline)
            all_results = pool.map(func, indices_and_tools)

        self._done = True
        slow_run_thread.join()

        if self.show_bars:
            if keep_bars:
                for _ in self._bars:
                    click.echo("", err=True)
            for b in self._bars:
                b.close()
            if keep_bars:
                # Progress bars terminate on whitespace
                bento.util.echo_newline()

        return all_results
