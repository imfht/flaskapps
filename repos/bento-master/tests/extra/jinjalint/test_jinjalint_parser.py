import os
from pathlib import Path

from bento.extra.jinjalint import JinjalintTool
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
    SIMPLE_INTEGRATION_PATH / "jinja-template.html",
]


def test_run(tmp_path: Path) -> None:
    tool = JinjalintTool(
        context_for(tmp_path, JinjalintTool.TOOL_ID, SIMPLE_INTEGRATION_PATH)
    )
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    expectation = [
        Violation(
            check_id="anchor-missing-noreferrer",
            tool_id=JinjalintTool.TOOL_ID,
            path="jinja-template.html",
            line=11,
            column=8,
            message="Pages opened with 'target=\"_blank\"' allow the new page to access the original's referrer. This can have privacy implications. Include 'rel=\"noreferrer\"' to prevent this.",
            severity=2,
            syntactic_context='        <a href="https://example.com" target="_blank">Test anchor</a>',
            link="https://bento.dev/checks/jinja/anchor-missing-noreferrer/",
        ),
        Violation(
            check_id="anchor-missing-noopener",
            tool_id=JinjalintTool.TOOL_ID,
            path="jinja-template.html",
            line=8,
            column=11,
            message="Pages opened with 'target=\"_blank\"' allow the new page to access the original's 'window.opener'. This can have security and performance implications. Include 'rel=\"noopener\"' to prevent this.",
            severity=2,
            syntactic_context='        <a href="https://example.com" target="_blank">Test anchor</a>',
            link="https://bento.dev/checks/jinja/anchor-missing-noopener/",
        ),
        Violation(
            check_id="form-missing-csrf-protection",
            tool_id=JinjalintTool.TOOL_ID,
            path="jinja-template.html",
            line=7,
            column=8,
            message="Flask apps using 'flask-wtf' require including a CSRF token in the HTML form. This check detects missing CSRF protection in HTML forms in Jinja templates.",
            severity=2,
            syntactic_context='        <form method="post">',
            link="https://bento.dev/checks/jinja/form-missing-csrf-protection/",
        ),
    ]

    assert set(violations) == set(expectation)  # Avoid ordering constraints with set
