import os
from pathlib import Path

from bento.extra.shellcheck import ShellcheckTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."
SHELL_INTEGRATION_PATH = BASE_PATH / "tests/integration/shell"
SHELL_TARGET = [
    SHELL_INTEGRATION_PATH / "bar",
    SHELL_INTEGRATION_PATH / "baz",
    SHELL_INTEGRATION_PATH / "foo",
    SHELL_INTEGRATION_PATH / "foo.sh",
    SHELL_INTEGRATION_PATH / "should_be_ignored",
    SHELL_INTEGRATION_PATH / "test.sh",
]


def test_run(tmp_path: Path) -> None:
    tool = ShellcheckTool(
        context_for(tmp_path, ShellcheckTool.tool_id(), SHELL_INTEGRATION_PATH)
    )
    tool.setup()
    violations = set(tool.results(SHELL_TARGET))
    assert violations == {
        Violation(
            tool_id="shellcheck",
            check_id="SC2068",
            path="foo.sh",
            line=3,
            column=6,
            message="Double quote array expansions to avoid re-splitting elements.",
            severity=2,
            syntactic_context="echo $@\n",
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC2068",
        ),
        Violation(
            tool_id="shellcheck",
            check_id="SC2068",
            path="foo",
            line=3,
            column=6,
            message="Double quote array expansions to avoid re-splitting elements.",
            severity=2,
            syntactic_context="echo $@\n",
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC2068",
        ),
        Violation(
            tool_id="shellcheck",
            check_id="SC2068",
            path="bar",
            line=3,
            column=6,
            message="Double quote array expansions to avoid re-splitting elements.",
            severity=2,
            syntactic_context="echo $@\n",
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC2068",
        ),
        Violation(
            tool_id="shellcheck",
            check_id="SC2068",
            path="baz",
            line=3,
            column=6,
            message="Double quote array expansions to avoid re-splitting elements.",
            severity=2,
            syntactic_context="echo $@\n",
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC2068",
        ),
        Violation(
            tool_id="shellcheck",
            check_id="SC1083",
            path="test.sh",
            line=5,
            column=33,
            message="This { is literal. Check expression (missing ;/\\n?) or quote it.",
            severity=1,
            syntactic_context='status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H "Content-Type:application/json" -d \'{\n',
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC1083",
        ),
        Violation(
            tool_id="shellcheck",
            check_id="SC1083",
            path="test.sh",
            line=5,
            column=43,
            message="This } is literal. Check expression (missing ;/\\n?) or quote it.",
            severity=1,
            syntactic_context='status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H "Content-Type:application/json" -d \'{\n',
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC1083",
        ),
    }
