import os
from pathlib import Path

from bento.extra.hadolint import HadolintTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."


def test_run(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests" / "integration" / "docker"
    tool = HadolintTool(context_for(tmp_path, HadolintTool.tool_id(), base_path))
    tool.setup()
    violations = tool.results([base_path / "foo.Dockerfile"])
    assert violations == [
        Violation(
            tool_id="hadolint",
            check_id="DL3006",
            path="foo.Dockerfile",
            line=1,
            column=1,
            message="Always tag the version of an image explicitly",
            severity=1,
            syntactic_context="FROM bar\n",
            filtered=None,
            link="https://github.com/hadolint/hadolint/wiki/DL3006",
        ),
        Violation(
            tool_id="hadolint",
            check_id="DL3002",
            path="foo.Dockerfile",
            line=3,
            column=1,
            message="Last USER should not be root",
            severity=1,
            syntactic_context="USER root\n",
            filtered=None,
            link="https://github.com/hadolint/hadolint/wiki/DL3002",
        ),
        Violation(
            tool_id="hadolint",
            check_id="SC2035",
            path="foo.Dockerfile",
            line=5,
            column=1,
            message="Use ./*glob* or -- *glob* so names with dashes won't become options.",
            severity=0,
            syntactic_context="RUN cp * /tmp/foo\n",
            filtered=None,
            link="https://github.com/koalaman/shellcheck/wiki/SC2035",
        ),
    ]
