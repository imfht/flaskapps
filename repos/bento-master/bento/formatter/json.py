import json
from typing import Any, Collection, Mapping, Sequence

from bento.formatter.base import FindingsMap, Formatter


class Json(Formatter):
    """Formats output as a single JSON blob."""

    @staticmethod
    def to_py(findings: FindingsMap) -> Sequence[Mapping[str, Any]]:
        return [
            {
                "tool_id": violation.tool_id,
                "check_id": violation.check_id,
                "line": violation.line,
                "column": violation.column,
                "message": violation.message,
                "severity": violation.severity,
                "path": violation.path,
            }
            for violations in findings.values()
            for violation in violations
        ]

    def dump(self, findings: FindingsMap) -> Collection[str]:
        return [json.dumps(self.to_py(findings))]
