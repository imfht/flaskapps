import os
from pathlib import Path

from bento.extra.dlint import DlintTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."
SIMPLE_INTEGRATION_PATH = BASE_PATH / "tests/integration/simple"
SIMPLE_TARGETS = [
    SIMPLE_INTEGRATION_PATH / "bar.py",
    SIMPLE_INTEGRATION_PATH / "baz.py",
    SIMPLE_INTEGRATION_PATH / "foo.py",
    SIMPLE_INTEGRATION_PATH / "init.js",
    SIMPLE_INTEGRATION_PATH / "package-lock.json",
    SIMPLE_INTEGRATION_PATH / "package.json",
]


def test_run(tmp_path: Path) -> None:
    tool = DlintTool(context_for(tmp_path, DlintTool.TOOL_ID, SIMPLE_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    expectation = [
        Violation(
            check_id="regular-expression-catastrophic-backtracking",
            tool_id=DlintTool.TOOL_ID,
            path="baz.py",
            line=4,
            column=0,
            message='catastrophic "re" usage - denial-of-service possible',
            severity=2,
            syntactic_context="re.search(r'(a+)+b', 'TEST')",
            link="https://github.com/dlint-py/dlint/blob/master/docs/linters/DUO138.md",
        )
    ]
    assert violations == expectation
