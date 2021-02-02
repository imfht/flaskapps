import json
import os
import subprocess
from pathlib import Path

from bento.extra.eslint import EslintParser, EslintTool
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
    with (THIS_PATH / "eslint_violation_simple.json").open() as json_file:
        data = json_file.read()

    result = EslintParser(BASE_PATH).parse(json.loads(data))

    expectation = [
        Violation(
            tool_id="eslint",
            check_id="no-console",
            path="tests/integration/simple/init.js",
            line=0,
            column=0,
            message="Unexpected console statement.",
            severity=1,
            syntactic_context="console.log(3)",
        ),
        Violation(
            tool_id="eslint",
            check_id="semi",
            path="tests/integration/simple/init.js",
            line=0,
            column=0,
            message="Missing semicolon.",
            severity=2,
            syntactic_context="console.log(3)",
        ),
    ]

    assert result == expectation


def test_line_move() -> None:
    parser = EslintParser(BASE_PATH)

    with (THIS_PATH / "eslint_violation_move_before.json").open() as json_file:
        before = parser.parse(json.loads(json_file.read()))
    with (THIS_PATH / "eslint_violation_move_after.json").open() as json_file:
        after = parser.parse(json.loads(json_file.read()))

    assert before == after
    assert [b.syntactic_identifier_str() for b in before] == [
        a.syntactic_identifier_str() for a in after
    ]


def test_run(tmp_path: Path) -> None:
    tool = EslintTool(
        context_for(tmp_path, EslintTool.ESLINT_TOOL_ID, SIMPLE_INTEGRATION_PATH)
    )
    tool.setup()
    try:
        violations = tool.results(SIMPLE_TARGETS)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e

    expectation = [
        Violation(
            tool_id="eslint",
            check_id="no-console",
            path="init.js",
            line=0,
            column=0,
            message="Unexpected console statement.",
            severity=1,
            syntactic_context="console.log(3)",
        ),
        Violation(
            tool_id="eslint",
            check_id="semi",
            path="init.js",
            line=0,
            column=0,
            message="Missing semicolon.",
            severity=2,
            syntactic_context="console.log(3)",
        ),
    ]

    assert violations == expectation


def test_typescript_run(tmp_path: Path) -> None:
    base_path = BASE_PATH / "tests/integration/js-and-ts"
    tool = EslintTool(context_for(tmp_path, EslintTool.ESLINT_TOOL_ID, base_path))
    tool.setup()
    try:
        violations = tool.results([base_path / "foo.ts"])
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e

    expectation = [
        Violation(
            tool_id="eslint",
            check_id="@typescript-eslint/no-unused-vars",
            path="foo.ts",
            line=1,
            column=7,
            message="'user' is assigned a value but never used.",
            severity=1,
            syntactic_context="const user: int = 'Mom'",
            filtered=None,
            link="https://eslint.org/docs/rules/@typescript-eslint/no-unused-vars",
        ),
        Violation(
            tool_id="eslint",
            check_id="semi",
            path="foo.ts",
            line=1,
            column=24,
            message="Missing semicolon.",
            severity=2,
            syntactic_context="const user: int = 'Mom'",
            filtered=None,
            link="https://eslint.org/docs/rules/semi",
        ),
    ]

    assert violations == expectation


# TODO I don't understand why this should not have any findings
# def test_jsx_run(tmp_path: Path) -> None:
#     base_path = BASE_PATH / "tests/integration/react"
#     tool = EslintTool(context_for(tmp_path, EslintTool.ESLINT_TOOL_ID, base_path))
#     tool.setup()
#     try:
#         violations = tool.results([base_path / "index.jsx"])
#     except subprocess.CalledProcessError as e:
#         raise e
#     assert violations == []


def test_file_match(tmp_path: Path) -> None:
    f = EslintTool(context_for(tmp_path, EslintTool.ESLINT_TOOL_ID)).file_name_filter

    assert f.match("js") is None
    assert f.match("foo.js") is not None
    assert f.match("foo.jsx") is not None
    assert f.match("foo.ts") is not None
    assert f.match("foo.tsx") is not None
    assert f.match("foo.jsa") is None


def test_missing_source() -> None:
    with (THIS_PATH / "eslint_violation_missing_source.json").open() as json_file:
        json_data = json_file.read()

    result = EslintParser(BASE_PATH).parse(json.loads(json_data))

    expectation = [
        Violation(
            tool_id="eslint",
            check_id="no-console",
            path="tests/integration/simple/init.js",
            line=0,
            column=0,
            message="Unexpected console statement.",
            severity=1,
            syntactic_context="",
        )
    ]

    assert result == expectation
