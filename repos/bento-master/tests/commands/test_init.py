from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from _pytest.monkeypatch import MonkeyPatch
from bento.commands.check import check
from bento.commands.init import InitCommand, init
from bento.context import Context
from tests.util import mod_file

INTEGRATION = Path(__file__).parent.parent / "integration"
SIMPLE = INTEGRATION / "simple"


def test_install_config() -> None:
    """Validates that bento installs a config file if none exists"""
    context = Context(base_path=SIMPLE, is_init=True)
    command = InitCommand(context)
    with mod_file(context.config_path):
        context.config_path.unlink()
        command._install_config_if_not_exists()
        cfg = context.config
        assert "eslint" in cfg["tools"]
        assert "flake8" in cfg["tools"]
        assert "bandit" in cfg["tools"]
        assert "dlint" in cfg["tools"]


def test_no_install_empty_project() -> None:
    """Validates that bento does installs a config on an empty project"""
    context = Context(base_path=INTEGRATION / "none", is_init=True)
    command = InitCommand(context)
    with mod_file(context.config_path):
        context.config_path.unlink()
        assert not context.config_path.exists()
        command._install_config_if_not_exists()
        assert len(context.config["tools"]) == 0


def test_install_ignore_in_repo() -> None:
    """Validates that bento installs an ignore file if none exists"""
    context = Context(base_path=SIMPLE, is_init=True)
    command = InitCommand(context)
    with mod_file(context.ignore_file_path):
        context.ignore_file_path.unlink()
        command._install_ignore_if_not_exists()
        context = Context(base_path=SIMPLE, is_init=True)
        assert context.ignore_file_path.exists()


def test_install_ignore_no_repo(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Validates that bento installs extra ignore items when not in a git repo"""
    monkeypatch.chdir(tmp_path)

    context = Context(base_path=tmp_path, is_init=True)
    assert not context.ignore_file_path.exists()
    command = InitCommand(context)
    command._install_ignore_if_not_exists()
    assert context.ignore_file_path.exists()
    with context.ignore_file_path.open() as file:
        patterns = file.read()

    assert "node_modules/" in patterns


def test_init_already_setup() -> None:
    context = Context(base_path=SIMPLE, is_init=True)
    result = CliRunner(mix_stderr=False).invoke(init, obj=context)

    expectation = """
╭──────────────────────────────────────────────────────────────────────────────╮
│                             Bento Initialization                             │
╰──────────────────────────────────────────────────────────────────────────────╯
Bento configures itself for personal use by default. This means that it:

1. Automatically checks for issues introduced by your code, as you commit it
2. Only affects you; it won’t change anything for other project contributors

Learn more about personal and team use at bento.dev/workflows.

Creating default ignore file at .bentoignore․․․․․․․․․․․․․․․․․․․․․ 👋 Skipped   
Creating default configuration at .bento/config.yml․․․․․․․․․․․․․․ 👋 Skipped   
Enabling autorun (see $ bento enable autorun --help)․․․․․․․․․․․․․ 👋 Skipped   
Creating GitHub Action configuration at .github/․․․․․․․․․․․․․․․․․ 👋 Skipped   

Bento initialized for Python and node-js (with react)

Installing tools:


╭──────────────────────────────────────────────────────────────────────────────╮
│                                  Thank You                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
From all of us at r2c, thank you for trying Bento! We can’t wait to hear what
you think.

Help and feedback: Reach out to us at support@r2c.dev or file an issue on
GitHub. We’d love to hear from you!

Community: Join #bento on our community Slack. Get support, talk with other
users, and share feedback.

Go forth and write great code! To use Bento:
  commit code․․․․․․․․․․․․․․․․․․․․․․․․․․․․․ $ git commit
  get help for a command․․․․․․․․․․․․․․․․․․ $ bento [COMMAND] --help

"""  # noqa - above string purposely contains trailing whitespace

    print(result.stderr)
    assert result.stderr == expectation


def test_init_js_only() -> None:
    context = Context(base_path=INTEGRATION / "js-and-ts", is_init=True)
    with mod_file(context.config_path):
        context.config_path.unlink()
        CliRunner(mix_stderr=False).invoke(init, obj=context)
        config = context.config

    assert "eslint" in config["tools"]
    assert "flake8" not in config["tools"]
    assert "bandit" not in config["tools"]
    assert "dlint" not in config["tools"]
    assert "r2c.jinja" not in config["tools"]


def test_init_py_only() -> None:
    context = Context(base_path=INTEGRATION / "py-only", is_init=True)
    with mod_file(context.config_path):
        context.config_path.unlink()
        CliRunner(mix_stderr=False).invoke(init, obj=context)
        config = context.config

    assert "eslint" not in config["tools"]
    assert "flake8" in config["tools"]
    assert "bandit" in config["tools"]
    assert "dlint" in config["tools"]


def test_init_clean(tmp_path: Path) -> None:
    """Validates that `init --clean` deletes tool virtual environments"""
    context = Context(base_path=INTEGRATION / "py-only", is_init=True)

    with patch("bento.constants.VENV_PATH", new=tmp_path):
        venv_file = tmp_path / "flake8" / "bin" / "activate"

        # Ensure venv is created
        CliRunner(mix_stderr=False).invoke(
            check, obj=context, args=["--all", str(context.base_path)]
        )
        assert venv_file.exists()

        # Ensure venv is corrupted, and not fixed with standard check
        venv_file.unlink()
        CliRunner(mix_stderr=False).invoke(
            check, obj=context, args=["--all", str(context.base_path)]
        )
        assert not venv_file.exists()

        # Ensure `init --clean` recreates venv
        CliRunner(mix_stderr=False).invoke(init, obj=context, args=["--clean"])
        assert venv_file.exists()
