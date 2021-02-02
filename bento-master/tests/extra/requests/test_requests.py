import os
from pathlib import Path

from bento.extra.requests import RequestsTool
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


def test_run_no_base_violations(tmp_path: Path) -> None:
    tool = RequestsTool(
        context_for(tmp_path, RequestsTool.TOOL_ID, SIMPLE_INTEGRATION_PATH)
    )
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    assert not violations


def test_run_flask_violations(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests/integration/requests"
    tool = RequestsTool(context_for(tmp_path, RequestsTool.TOOL_ID, base_path))
    tool.setup()
    violations = tool.results([base_path / "bad.py"])

    expectation = [
        Violation(
            tool_id="r2c.requests",
            check_id="use-timeout",
            path="bad.py",
            line=3,
            column=5,
            message="requests will hang forever without a timeout. Consider adding a timeout (recommended 10 sec).",
            severity=2,
            syntactic_context="r = requests.get('http://MYURL.com', auth=('user', 'pass'))",
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-requests/use-timeout",
        ),
        Violation(
            tool_id="r2c.requests",
            check_id="no-auth-over-http",
            path="bad.py",
            line=3,
            column=5,
            message="auth is possibly used over http://, which could expose credentials. possible_urls: ['http://MYURL.com']",
            severity=2,
            syntactic_context="r = requests.get('http://MYURL.com', auth=('user', 'pass'))",
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-requests/no-auth-over-http",
        ),
    ]

    violations_important_info = set(
        map(
            lambda viol: (viol.tool_id, viol.check_id, viol.line, viol.column),
            violations,
        )
    )
    expectation_important_info = set(
        map(
            lambda viol: (viol.tool_id, viol.check_id, viol.line, viol.column),
            expectation,
        )
    )
    assert violations_important_info == expectation_important_info
