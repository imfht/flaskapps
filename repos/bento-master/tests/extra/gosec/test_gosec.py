import os
from pathlib import Path

from bento.extra.gosec import GosecTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."


def test_run(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests" / "integration" / "go"
    tool = GosecTool(context_for(tmp_path, GosecTool.tool_id(), base_path))
    tool.setup()
    violations = tool.results([base_path / "bad.go"])
    assert violations == [
        Violation(
            tool_id="gosec",
            check_id="G101",
            path="bad.go",
            line=7,
            column=2,
            message="Potential hardcoded credentials",
            severity=2,
            syntactic_context='password := "f62e5bcda4fae4f82370da0c6f20697b8f8447ef"\n',
            filtered=None,
            link="https://cwe.mitre.org/data/definitions/798.html",
        )
    ]


def test_file_selection(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests" / "integration" / "go"
    tool = GosecTool(context_for(tmp_path, GosecTool.tool_id(), base_path))
    tool.setup()
    violations = tool.results([base_path / "ok.go"])
    assert violations == []
