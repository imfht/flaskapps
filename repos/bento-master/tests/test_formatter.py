import json

import bento.formatter
from bento.base_context import BaseContext
from bento.violation import Violation
from tests.util import strip_ansi

VIOLATIONS = {
    "r2c.eslint": [
        Violation(
            tool_id="r2c.eslint",
            check_id="no-console",
            path="bento/test/integration/init.js",
            line=0,
            column=0,
            severity=1,
            message="Unexpected console statement.",
            syntactic_context="console.log(3)",
            link="https://eslint.org/docs/rules/no-console",
        ),
        Violation(
            tool_id="r2c.eslint",
            check_id="semi",
            path="bento/test/integration/init.js",
            line=0,
            column=0,
            message="Missing semicolon.",
            severity=2,
            syntactic_context="console.log(3)",
            link="https://eslint.org/docs/rules/semi",
        ),
    ]
}


NULL_CONTEXT = BaseContext()


def test_stylish_formatter() -> None:
    stylish = bento.formatter.for_name("stylish", NULL_CONTEXT, {})
    output = [strip_ansi(line) for line in stylish.dump(VIOLATIONS)]
    expectation = [
        "bento/test/integration/init.js",
        f"   0:0  Missing semicolon.                       r2c.eslint     semi https://eslint.org/docs/rules/semi",
        f"   0:0  Unexpected console statement.            r2c.eslint     no-console https://eslint.org/docs/rules/no-console",
        "",
    ]

    assert output == expectation


def test_clippy_formatter() -> None:
    clippy = bento.formatter.for_name("clippy", NULL_CONTEXT, {})
    output = [strip_ansi(line) for line in clippy.dump(VIOLATIONS)]
    expectation = [
        "r2c.eslint semi https://eslint.org/docs/rules/semi",
        "     > bento/test/integration/init.js:0",
        "     ╷",
        "    0│   console.log(3)",
        "     ╵",
        "     = Missing semicolon.",
        "",
        "r2c.eslint no-console https://eslint.org/docs/rules/no-console",
        "     > bento/test/integration/init.js:0",
        "     ╷",
        "    0│   console.log(3)",
        "     ╵",
        "     = Unexpected console statement.",
        "",
    ]
    print(output)
    assert output == expectation


def test_json_formatter() -> None:
    json_formatter = bento.formatter.for_name("json", NULL_CONTEXT, {})
    json_formatter.config = {}
    output = json.loads(next(iter(json_formatter.dump(VIOLATIONS))))
    assert output == [
        {
            "tool_id": "r2c.eslint",
            "check_id": "no-console",
            "line": 0,
            "column": 0,
            "severity": 1,
            "message": "Unexpected console statement.",
            "path": "bento/test/integration/init.js",
        },
        {
            "tool_id": "r2c.eslint",
            "check_id": "semi",
            "path": "bento/test/integration/init.js",
            "line": 0,
            "column": 0,
            "severity": 2,
            "message": "Missing semicolon.",
        },
    ]


def test_histo_formatter() -> None:
    expectation = """r2c.eslint:
  no-console     1▕▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
  semi           1▕▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
"""

    histo_formatter = bento.formatter.for_name("histo", NULL_CONTEXT, {})
    output = "\n".join(histo_formatter.dump(VIOLATIONS))

    assert strip_ansi(output) == expectation
