import os
from pathlib import Path

from bento.extra.bandit import BanditTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."
SIMPLE_INTEGRATION_PATH = BASE_PATH / "tests/integration/simple"
SIMPLE_TARGETS = [
    SIMPLE_INTEGRATION_PATH / "bar.py",
    SIMPLE_INTEGRATION_PATH / "foo.py",
    SIMPLE_INTEGRATION_PATH / "init.js",
    SIMPLE_INTEGRATION_PATH / "package-lock.json",
    SIMPLE_INTEGRATION_PATH / "package.json",
]


def test_run(tmp_path: Path) -> None:
    tool = BanditTool(
        context_for(tmp_path, BanditTool.TOOL_ID, SIMPLE_INTEGRATION_PATH)
    )
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    expectation = [
        Violation(
            check_id="error",
            tool_id=BanditTool.TOOL_ID,
            path="foo.py",
            line=0,
            column=0,
            message="syntax error while parsing AST from file",
            severity=4,
            syntactic_context="",
            link=None,
        ),
        Violation(
            check_id="import-subprocess",
            tool_id=BanditTool.TOOL_ID,
            path="bar.py",
            line=1,
            column=0,
            message="Consider possible security implications associated with subprocess module.",
            severity=1,
            syntactic_context=" import subprocess",
            link="https://bandit.readthedocs.io/en/latest/blacklists/blacklist_imports.html#b404-import-subprocess",
        ),
        Violation(
            check_id="subprocess-popen-with-shell-equals-true",
            tool_id=BanditTool.TOOL_ID,
            path="bar.py",
            line=4,
            column=0,
            message="subprocess call with shell=True identified, security issue.",
            severity=3,
            syntactic_context='     subprocess.run(f"bash -c {cmd}", shell=True)',
            link="https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html",
        ),
    ]

    assert violations == expectation
