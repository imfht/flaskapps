import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, cast

from bento.extra.sgrep import SgrepTool
from bento.violation import Violation
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."
SGREP_PATH = BASE_PATH / "tests/integration/sgrep"

REMOTE_DOCKER_ENV = "R2C_USE_REMOTE_DOCKER"


@contextmanager
def _remote_docker() -> Iterator[None]:
    previous = os.environ.get(REMOTE_DOCKER_ENV)
    try:
        os.environ[REMOTE_DOCKER_ENV] = "1"
        yield
    finally:
        if previous is not None:
            os.environ[REMOTE_DOCKER_ENV] = previous
        else:
            os.unsetenv(REMOTE_DOCKER_ENV)


def test_run(tmp_path: Path) -> None:
    tool = SgrepTool(context_for(tmp_path, SgrepTool.tool_id(), SGREP_PATH))
    shutil.copy(
        SGREP_PATH / ".bento" / "sgrep.yml", tool.context.resource_path / "sgrep.yml"
    )

    with _remote_docker():
        tool.setup()
        violations = set(tool.results([SGREP_PATH / "flask_configs.py"]))

    print(violations)
    expectation = {
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_DEBUG",
            path="flask_configs.py",
            line=33,
            column=1,
            message="Hardcoded variable `DEBUG` detected. Set this by using FLASK_DEBUG environment variable",
            severity=2,
            syntactic_context='app.config["DEBUG"] = False',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_DEBUG",
            path="flask_configs.py",
            line=31,
            column=1,
            message="Hardcoded variable `DEBUG` detected. Set this by using FLASK_DEBUG environment variable",
            severity=2,
            syntactic_context='app.config["DEBUG"] = True',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_ENV",
            path="flask_configs.py",
            line=27,
            column=1,
            message="Hardcoded variable `ENV` detected. Set this by using FLASK_ENV environment variable",
            severity=2,
            syntactic_context='app.config["ENV"] = "production"',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_ENV",
            path="flask_configs.py",
            line=25,
            column=1,
            message="Hardcoded variable `ENV` detected. Set this by using FLASK_ENV environment variable",
            severity=2,
            syntactic_context='app.config["ENV"] = "development"',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_SECRET_KEY",
            path="flask_configs.py",
            line=19,
            column=1,
            message="Hardcoded variable `SECRET_KEY` detected. Use environment variables or config files instead",
            severity=2,
            syntactic_context='app.config.update(SECRET_KEY="aaaa")',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_TESTING",
            path="flask_configs.py",
            line=15,
            column=1,
            message="Hardcoded variable `TESTING` detected. Use environment variables or config files instead",
            severity=2,
            syntactic_context="app.config.update(TESTING=True)",
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_TESTING",
            path="flask_configs.py",
            line=13,
            column=1,
            message="Hardcoded variable `TESTING` detected. Use environment variables or config files instead",
            severity=2,
            syntactic_context='app.config["TESTING"] = False',
            filtered=None,
            link=None,
        ),
        Violation(
            tool_id="sgrep",
            check_id="bento.avoid_hardcoded_config_TESTING",
            path="flask_configs.py",
            line=11,
            column=1,
            message="Hardcoded variable `TESTING` detected. Use environment variables or config files instead",
            severity=2,
            syntactic_context='app.config["TESTING"] = True',
            filtered=None,
            link=None,
        ),
    }

    assert violations == expectation


def test_cache_invalidation(tmp_path: Path) -> None:
    tool = SgrepTool(context_for(tmp_path, SgrepTool.tool_id(), SGREP_PATH))
    template_path = SGREP_PATH / ".bento" / "sgrep.yml"
    config_path = cast(Path, tool.get_config_path())

    shutil.copy(template_path, config_path)

    with _remote_docker():
        tool.setup()

        violations = set(tool.results([SGREP_PATH / "flask_configs.py"]))
        assert len(violations) == 8

        config_path.unlink()

        violations = set(tool.results([SGREP_PATH / "flask_configs.py"]))
        assert len(violations) == 0
