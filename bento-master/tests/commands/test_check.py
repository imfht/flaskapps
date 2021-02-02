import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

import bento.constants
import bento.extra.eslint
import bento.result
import bento.tool_runner
from _pytest.monkeypatch import MonkeyPatch
from bento.commands.check import check
from bento.context import Context
from tests.util import mod_file

BASE = Path(__file__).parent.parent.parent
INTEGRATION = BASE / "tests" / "integration"
SIMPLE = INTEGRATION / "simple"


def test_check_compare_archive() -> None:
    """Validates that check discovers issues in tech debt mode"""

    runner = CliRunner(mix_stderr=False)
    Context(SIMPLE).cache.wipe()

    result = runner.invoke(
        check,
        ["--formatter", "json", "--all", str(SIMPLE)],
        obj=Context(base_path=SIMPLE),
    )
    parsed = json.loads(result.stdout)
    assert len(parsed) == 4


def test_check_no_diff_noop() -> None:
    """Validates that bare check with no diffs is noop"""

    runner = CliRunner(mix_stderr=False)
    Context(SIMPLE).cache.wipe()

    result = runner.invoke(
        check, ["--formatter", "json"], obj=Context(base_path=SIMPLE)
    )

    parsed = json.loads(result.stdout)
    assert len(parsed) == 0

    assert (
        "Nothing to check or archive. Please confirm that changes are staged and not"
        in result.stderr
    )


def test_check_specified_paths(monkeypatch: MonkeyPatch) -> None:
    """Validates that check discovers issues in specified paths"""

    monkeypatch.chdir(SIMPLE)
    runner = CliRunner(mix_stderr=False)
    Context(SIMPLE).cache.wipe()

    result = runner.invoke(
        check,
        ["--formatter", "json", "--all", "init.js", "foo.py"],
        obj=Context(base_path=SIMPLE),
    )
    parsed = json.loads(result.stdout)
    assert len(parsed) == 3


def test_check_compare_to_head_no_diffs() -> None:
    """Validates that check shows no issues with no diffs with --comparison head"""

    runner = CliRunner(mix_stderr=False)
    Context(SIMPLE).cache.wipe()

    result = runner.invoke(
        check, ["--formatter", "json", str(SIMPLE)], obj=Context(base_path=SIMPLE)
    )
    parsed = json.loads(result.stdout)
    assert len(parsed) == 0


def test_check_compare_to_head_diffs(monkeypatch: MonkeyPatch) -> None:
    """ Validates that check shows issues in staged changes
        Note that this check fails if there are any locally staged changes
    """
    monkeypatch.chdir(SIMPLE)
    runner = CliRunner(mix_stderr=False)
    Context(SIMPLE).cache.wipe()

    edited = SIMPLE / "bar.py"

    with mod_file(edited):
        with edited.open("a") as stream:
            stream.write("\nprint({'a': 2}).has_key('b')")

        subprocess.run(["git", "add", str(edited)], check=True)
        result = runner.invoke(
            check, ["--formatter", "json", str(SIMPLE)], obj=Context(base_path=SIMPLE)
        )
        subprocess.run(["git", "reset", "HEAD", str(edited)])

    parsed = json.loads(result.stdout)
    assert [p["check_id"] for p in parsed] == ["deprecated-has-key"]


def test_check_specified_ignored(monkeypatch: MonkeyPatch) -> None:
    """Validates that check does not check specified, ignored paths"""

    monkeypatch.chdir(BASE)
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(
        check,
        ["-f", "json", "--all", "tests/integration/simple/bar.py"],
        obj=Context(base_path=BASE),
    )
    parsed = json.loads(result.stdout)
    assert not parsed


def test_check_relative_path(monkeypatch: MonkeyPatch) -> None:
    """Validates that check works with relative specified paths when not run from project root"""

    monkeypatch.chdir(SIMPLE / "dist")
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(
        check, ["-f", "json", "--all", "../bar.py"], obj=Context(base_path=SIMPLE)
    )
    parsed = json.loads(result.stdout)
    print(parsed)
    assert len(parsed) == 1


def test_check_no_archive() -> None:
    """Validates that check operates without an archive file"""

    runner = CliRunner(mix_stderr=False)
    context = Context(base_path=SIMPLE)
    context.cache.wipe()

    with mod_file(context.baseline_file_path):
        context.baseline_file_path.unlink()
        result = runner.invoke(
            check,
            ["--formatter", "json", "--all", str(SIMPLE)],
            obj=Context(base_path=SIMPLE),
        )
        parsed = json.loads(result.stdout)
        assert len(parsed) == 5  # Archive contains a single whitelisted finding


def test_check_no_init() -> None:
    """Validates that check fails when no configuration file"""

    runner = CliRunner()
    Context(INTEGRATION).cache.wipe()
    # No .bento.yml exists in this directory
    result = runner.invoke(check, obj=Context(base_path=INTEGRATION))
    assert result.exception.code == 3


def test_check_tool_error() -> None:
    expectation = "✘ Error while running r2c.foo: test"

    with patch.object(
        bento.tool_runner.Runner,
        "parallel_results",
        return_value=[("r2c.foo", Exception("test"))],
    ):
        runner = CliRunner(mix_stderr=False)
        Context(SIMPLE).cache.wipe()

        result = runner.invoke(
            check, ["--all", str(SIMPLE)], obj=Context(base_path=SIMPLE)
        )
        print(result.stderr)
        assert result.exception.code == 3
        assert expectation in result.stderr.splitlines()
