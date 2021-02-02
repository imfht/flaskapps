import itertools
import shutil
import textwrap
from typing import Collection, List

import click

from bento.formatter.base import FindingsMap, Formatter
from bento.util import ANSI_WIDTH, PRINT_WIDTH, render_link
from bento.violation import Violation


class Stylish(Formatter):
    """
    Mimics the eslint "stylish" formatter
    """

    TERM_WIDTH, _ = shutil.get_terminal_size((PRINT_WIDTH, 0))

    @staticmethod
    def __print_path(path: str) -> str:
        return path

    def __print_violation(self, violation: Violation) -> List[str]:
        message_len = max(Stylish.TERM_WIDTH - 50, 40)

        line = f"{violation.line:>4d}"
        col = f"{violation.column:<2d}"
        tool_id = f"{violation.tool_id:<14s}"
        rule = f"{violation.check_id:s}"

        message = textwrap.wrap(violation.message.strip(), message_len)

        if not violation.link:
            link = rule
        else:
            link = render_link(rule, violation.link)

        out = [
            f"{line}:{col} {click.style(message[0], dim=True):<{message_len + 2 * ANSI_WIDTH}s} {tool_id} {link}"
        ]
        for m in message[1:]:
            out.append(
                f"        {click.style(m, dim=True):<{message_len + 2 * ANSI_WIDTH}s}"
            )

        return out

    def dump(self, findings: FindingsMap) -> Collection[str]:
        violations = self.by_path(findings)
        lines = []

        ordered: List[Violation] = sorted(violations, key=Formatter.path_of)
        for path, vv in itertools.groupby(ordered, Formatter.path_of):
            lines.append(Stylish.__print_path(path))
            for v in sorted(vv, key=lambda v: (v.line, v.column, v.message)):
                lines += self.__print_violation(v)
            lines.append("")

        return lines
