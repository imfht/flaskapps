import itertools
from typing import Collection, List, Optional

import attr
import click

from bento.formatter.base import FindingsMap, Formatter
from bento.util import PRINT_WIDTH, render_link
from bento.violation import Violation


@attr.s(auto_attribs=True)
class Hit:
    check_id: str
    link: Optional[str]
    count: int  # Number of findings for this check


@attr.s(auto_attribs=True)
class ToolHits:
    tool_id: str
    hits: List[Hit]  # Ordered list of Hit objects for this tool
    max_count = 0
    max_check_width = 0

    def __attrs_post_init__(self) -> None:
        if self.hits:
            self.max_count = max(h.count for h in self.hits)
            self.max_check_width = max(len(h.check_id) for h in self.hits)


class Histo(Formatter):
    """Formats output as a histogram."""

    MAX_HISTO_PER_TOOL = 5
    MIN_CHECK_WIDTH = 10
    MAX_CHECK_WIDTH = 35
    OTHER = "Other"

    @staticmethod
    def _render_bar(count: int, max_count: int, bar_width: int) -> str:
        return "▕" + "".ljust(int(round(bar_width * count / max_count)), "▬")

    def _max_bars_per_tool(self) -> int:
        return int(self.config.get("bars-per-tool", Histo.MAX_HISTO_PER_TOOL))

    def _render_hit(self, hit: Hit, max_count: int, check_width: int) -> str:
        bar_width = (
            PRINT_WIDTH - check_width - 10
        )  # 5 for check, 5 for fixed characters
        check_str = click.style(
            render_link(
                hit.check_id[:check_width],
                href=hit.link,
                print_alternative=False,
                width=check_width,
            )
        )
        count_str = click.style(f"{hit.count:>5d}", dim=True)
        bar = click.style(Histo._render_bar(hit.count, max_count, bar_width), dim=True)
        return f"  {check_str} {count_str}{bar}"

    def _tool_hits(self, tool_id: str, violations: Collection[Violation]) -> ToolHits:
        """
        Collects top hits for a single tool.
        """
        keyfunc = lambda v: v.check_id  # noqa
        sorted_violations = sorted(violations, key=keyfunc)
        counts = sorted(
            (
                Hit(check_id.strip(), next(vv).link, 1 + sum(1 for _ in vv))
                for check_id, vv in itertools.groupby(sorted_violations, keyfunc)
            ),
            key=(lambda hit: hit.count),
            reverse=True,
        )
        top = counts[0 : self._max_bars_per_tool()]
        n_top = sum(h.count for h in top)

        # Add remaining hits as "Other" if more hits than max_bars_per_tool
        if len(counts) > len(top):
            top.append(Hit(Histo.OTHER, None, len(violations) - n_top))

        return ToolHits(tool_id, top)

    def _all_hits(self, findings: FindingsMap) -> List[ToolHits]:
        """
        For each tool, returns an ordered list of (ToolId, CheckData, max(Count)).

        Each list is the top checks by finding count, plus an "Other" row if more than MAX_HISTO_PER_TOOL checks fired.
        """
        return [
            self._tool_hits(tool_id, violations)
            for tool_id, violations in findings.items()
        ]

    def dump(self, findings: FindingsMap) -> Collection[str]:
        """
        Prints an ordered histogram of "top hits" per tool.

        E.g.:
            r2c.eslint:
              no-undef                  16015 ++++++++++++++++++++++++++++++++++++++++++++++++++
              no-var                     7880 ++++++++++++++++++++++++
              @typescript-eslint/explic  4864 +++++++++++++++
              object-shorthand           1399 ++++
              @typescript-eslint/no-var   157
              Other                      1178 +++

            r2c.flake8:
              B008:                       453 +
              A003                        103
              F405                         62
              B007                         56
              B006                         52
              Other                       116
        """
        if not findings:
            return []

        all_hits = self._all_hits(findings)
        max_count = max(h.max_count for h in all_hits)
        check_width = max(h.max_check_width for h in all_hits)
        check_width = max(
            min(check_width, Histo.MAX_CHECK_WIDTH), Histo.MIN_CHECK_WIDTH
        )
        out = []
        for tool_hits in sorted(all_hits, key=(lambda h: h.max_count), reverse=True):
            if tool_hits.hits:
                out.append(click.style(f"{tool_hits.tool_id}:", bold=True))
                for hit in tool_hits.hits:
                    out.append(self._render_hit(hit, max_count, check_width))
                out.append("")
        return out
