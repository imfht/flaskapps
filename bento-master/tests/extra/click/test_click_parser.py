import os
from pathlib import Path

from bento.extra.click import ClickParser, ClickTool
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
CLICK_INTEGRATION_PATH = BASE_PATH / "tests/integration/click"
CLICK_TARGETS = [CLICK_INTEGRATION_PATH / "bad_examples.py"]

EXPECTATIONS = [
    Violation(
        tool_id="r2c.click",
        check_id="option-function-argument-check",
        path="bad_examples.py",
        line=12,
        column=1,
        message="function `bad_option_one` missing parameter `d` for `@click.option`",
        severity=2,
        syntactic_context="@click.command()",
        filtered=None,
        link="",
    ),
    Violation(
        tool_id="r2c.click",
        check_id="names-are-well-formed",
        path="bad_examples.py",
        line=19,
        column=1,
        message="option 'd' should begin with a '-'",
        severity=2,
        syntactic_context="@click.command()",
        filtered=None,
        link="",
    ),
    Violation(
        tool_id="r2c.click",
        check_id="names-are-well-formed",
        line=26,
        path="bad_examples.py",
        column=1,
        message="argument '-a' should not begin with a '-'",
        severity=2,
        syntactic_context="@click.command()",
        filtered=None,
        link="",
    ),
    Violation(
        tool_id="r2c.click",
        check_id="names-are-well-formed",
        path="bad_examples.py",
        line=33,
        column=1,
        message="missing parameter name",
        severity=2,
        syntactic_context="@click.command()",
        filtered=None,
        link="",
    ),
    Violation(
        tool_id="r2c.click",
        check_id="launch-uses-literal",
        path="bad_examples.py",
        line=41,
        column=5,
        message="calls to click.launch() should use literal urls to prevent arbitrary site redirects",
        severity=2,
        syntactic_context="    click.launch(x)",
        filtered=None,
        link="",
    ),
]


def test_parse() -> None:
    with (THIS_PATH / "click_violation_simple.json").open() as json_file:
        json = json_file.read()

    result = ClickParser(BASE_PATH).parse(json)
    assert result == EXPECTATIONS


def test_run_no_base_violations(tmp_path: Path) -> None:
    tool = ClickTool(context_for(tmp_path, ClickTool.TOOL_ID, SIMPLE_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(SIMPLE_TARGETS)

    assert not violations


def test_run_click_violations(tmp_path: Path) -> None:
    tool = ClickTool(context_for(tmp_path, ClickTool.TOOL_ID, CLICK_INTEGRATION_PATH))
    tool.setup()
    violations = tool.results(CLICK_TARGETS)
    assert violations == EXPECTATIONS
