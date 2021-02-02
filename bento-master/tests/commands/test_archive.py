from pathlib import Path

from click.testing import CliRunner

import bento.extra.eslint
import bento.result
import bento.tool_runner
from bento.commands.archive import archive
from bento.context import Context
from tests.util import mod_file

INTEGRATION = Path(__file__).parent.parent / "integration"


def test_archive_no_init() -> None:
    """Validates that archive fails when no configuration file"""

    runner = CliRunner()
    # No .bento.yml exists in this directory
    result = runner.invoke(
        archive, obj=Context(base_path=INTEGRATION), catch_exceptions=True
    )
    assert result.exception.code == 3


def test_archive_updates_whitelist() -> None:
    """Validates that archive updates the whitelist file"""

    runner = CliRunner()

    context = Context(INTEGRATION / "simple")

    with mod_file(context.baseline_file_path) as whitelist:
        runner.invoke(archive, obj=context, args=["--all", str(context.base_path)])
        yml = bento.result.json_to_violation_hashes(whitelist)

    expectation = {
        "bandit": {
            "6f77d9d773cc5248ae20b83f80a7b26a",
            "e540c501c568dad8d9e2e00abba5740f",
        },
        "eslint": {"6daebd293be00a3d97e19de4a1a39fa5"},
        "flake8": {
            "23d898269aae05ed6897cf56dfbd3cde",
            "b849b45f8a969cc5eb46e6ea76d7e809",
        },
    }

    assert yml == expectation
