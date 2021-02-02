import os
from pathlib import Path

from bento.extra.boto3 import Boto3Parser, Boto3Tool
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
BOTO3_INTEGRATION_PATH = BASE_PATH / "tests/integration/boto3"
BOTO3_TARGETS = [BOTO3_INTEGRATION_PATH / "bad.py"]


def test_parse() -> None:
    with (THIS_PATH / "boto3_violation_simple.json").open() as json_file:
        json = json_file.read()

    result = Boto3Parser(BASE_PATH).parse(json)

    expectation = [
        Violation(
            tool_id="r2c.boto3",
            check_id="hardcoded-access-token",
            path="bad.py",
            line=4,
            column=1,
            message="Hardcoded access token detected. Consider using a config file or environment variables.",
            severity=2,
            syntactic_context="Session(aws_access_key_id='AKIA1235678901234567',",
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-boto3/hardcoded-access-token",
        )
    ]

    assert result == expectation


def test_run_no_base_violations(tmp_path: Path) -> None:
    tool = Boto3Tool(context_for(tmp_path, Boto3Tool.TOOL_ID, SIMPLE_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    assert not violations


def test_run_flask_violations(tmp_path: Path) -> None:
    tool = Boto3Tool(context_for(tmp_path, Boto3Tool.TOOL_ID, BOTO3_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(BOTO3_TARGETS)

    expectation = [
        Violation(
            tool_id="r2c.boto3",
            check_id="hardcoded-access-token",
            path="bad.py",
            line=4,
            column=11,
            message="Hardcoded access token detected. Consider using a config file or environment variables.",
            severity=2,
            syntactic_context="session = Session(aws_access_key_id='AKIA1235678901234567',",
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-boto3/hardcoded-access-token",
        )
    ]

    assert violations == expectation
