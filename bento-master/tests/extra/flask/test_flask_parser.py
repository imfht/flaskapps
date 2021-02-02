import os
from pathlib import Path

from bento.extra.flask import FlaskParser, FlaskTool
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


def test_parse() -> None:
    with (THIS_PATH / "flask_violation_simple.json").open() as json_file:
        json = json_file.read()

    result = FlaskParser(BASE_PATH).parse(json)

    expectation = [
        Violation(
            tool_id="r2c.flask",
            check_id="send-file-open",
            path="bad.py",
            line=4,
            column=1,
            message="Passing a file-like object to flask.send_file without the mimetype or attachment_filename keyword arg will raise a ValueError. If you are sending a static file, pass in a string path to the file instead. Otherwise, specify a mimetype or attachment_filename in flask.send_file.",
            severity=2,
            syntactic_context='flask.send_file(open("file.txt"))',
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-flask/send-file-open",
        )
    ]

    assert result == expectation


def test_run_no_base_violations(tmp_path: Path) -> None:
    tool = FlaskTool(context_for(tmp_path, FlaskTool.TOOL_ID, SIMPLE_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    assert not violations


def test_run_flask_violations(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests/integration/flask"
    tool = FlaskTool(context_for(tmp_path, FlaskTool.TOOL_ID, base_path))
    tool.setup()
    violations = tool.results([base_path / "bad.py"])

    expectation = [
        Violation(
            tool_id="r2c.flask",
            check_id="send-file-open",
            path="bad.py",
            line=4,
            column=1,
            message="Passing a file-like object to flask.send_file without the mimetype or attachment_filename keyword arg will raise a ValueError. If you are sending a static file, pass in a string path to the file instead. Otherwise, specify a mimetype or attachment_filename in flask.send_file.",
            severity=2,
            syntactic_context='flask.send_file(open("file.txt"))',
            filtered=None,
            link="https://bento.dev/checks/en/latest/flake8-flask/send-file-open",
        )
    ]

    assert violations == expectation
