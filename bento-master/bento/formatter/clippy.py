import itertools
import shutil
import sys
import textwrap
from typing import Collection, List

import click

from bento.formatter.base import FindingsMap, Formatter
from bento.util import PRINT_WIDTH, render_link
from bento.violation import Violation


class Clippy(Formatter):
    """
    Mimics the clippy formatter
    """

    PIPE = click.style("│", dim=True)
    CONTEXT_HEADER = f"     {click.style('╷', dim=True)}"
    CONTEXT_FOOTER = f"     {click.style('╵', dim=True)}"
    NOTE_LEADER = f"     = "
    LEADER_LEN = len(NOTE_LEADER)
    MESSAGE_OVERFLOW_LEADER = "".ljust(len(NOTE_LEADER), " ")
    MIN_MESSAGE_LEN = 40

    @staticmethod
    def _print_path(path: str, line: int, col: int) -> str:
        fpos = click.style(f"{path}:{line}")
        return f"     > {fpos}"

    def _print_violation(self, violation: Violation, max_message_len: int) -> List[str]:
        message_lines = textwrap.wrap(violation.message.strip(), width=max_message_len)

        out = []

        # Strip so trailing newlines are not printed out
        stripped = violation.syntactic_context.rstrip()
        context = [line.rstrip() for line in stripped.split("\n")]

        if stripped:
            out.append(Clippy.CONTEXT_HEADER)
            for offset, line in enumerate(context):
                line_no = click.style(f"{violation.line + offset:>4d}", dim=True)
                out.append(f" {line_no}{Clippy.PIPE}   {line}")
            out.append(Clippy.CONTEXT_FOOTER)

        out.append(f"{Clippy.NOTE_LEADER}{click.style(message_lines[0], dim=True)}")
        for mline in message_lines[1:]:
            out.append(
                f"{Clippy.MESSAGE_OVERFLOW_LEADER}{click.style(mline, dim=True)}"
            )

        return out

    def _print_error_message(self, violation: Violation) -> str:
        tool_id = f"{violation.tool_id}".strip()
        rule = f"{violation.check_id}".strip()

        link = render_link(rule, violation.link)

        return f"{Clippy.BOLD}{tool_id} {link}{Clippy.END}"

    def dump(self, findings: FindingsMap) -> Collection[str]:
        if not findings:
            return []

        lines = []
        violations = self.by_path(findings)
        max_message_len = min(
            max((len(v.message) for v in violations), default=0),
            PRINT_WIDTH - Clippy.LEADER_LEN,
        )

        if sys.stdout.isatty():
            terminal_width, _ = shutil.get_terminal_size((PRINT_WIDTH, 0))
            max_message_len = max(
                min(max_message_len, terminal_width - Clippy.LEADER_LEN),
                Clippy.MIN_MESSAGE_LEN,
            )

        ordered: List[Violation] = sorted(violations, key=Formatter.path_of)

        for path, vv in itertools.groupby(ordered, Formatter.path_of):
            for v in sorted(vv, key=lambda v: (v.line, v.column, v.message)):
                lines.append(self._print_error_message(v))
                lines.append(Clippy._print_path(path, v.line, v.column))

                lines += self._print_violation(v, max_message_len)
                lines.append("")

        return lines
