from pathlib import Path

from click.testing import CliRunner

import bento.cli
import bento.constants as constants
from _pytest.monkeypatch import MonkeyPatch
from bento import __version__
from bento.cli import cli
from bento.context import Context
from tests.util import strip_ansi

INTEGRATION = Path(__file__).parent.parent / "integration"
SIMPLE = INTEGRATION / "simple"
PY_ONLY = INTEGRATION / "py-only"


def test_upgrade_banner(monkeypatch: MonkeyPatch) -> None:
    """Validates that the upgrade banner is printed to standard error"""

    monkeypatch.setattr(bento.cli, "_is_running_latest", lambda: False)
    monkeypatch.setattr(bento.cli, "_is_test", lambda: False)

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["--agree", "--email", constants.QA_TEST_EMAIL_ADDRESS, "check", "--help"]
    )

    # result.stderr is stripped of color characters by piping

    assert result.stderr.rstrip() == strip_ansi(
        constants.UPGRADE_WARNING_OUTPUT.rstrip()
    )


def test_version() -> None:
    """Validates that version string is printed"""

    runner = CliRunner()
    context = Context(base_path=SIMPLE)

    result = runner.invoke(cli, ["--version"], obj=context)
    assert result.output.strip() == f"bento/{__version__}"
