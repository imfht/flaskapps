import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator

import yaml
from git import Repo

import pytest
from bento.commands import ci as uut
from bento.context import Context


@dataclass
class Paths:
    """Helper class for easily finding paths of interest in the passed repo."""

    repo: Repo

    @property
    def repo_path(self) -> Path:
        return Path(self.repo.working_dir)

    @property
    def workflows_path(self) -> Path:
        return self.repo_path / ".github" / "workflows"

    @property
    def workflow_path(self) -> Path:
        return self.workflows_path / "bento.yml"


def _bento_step(workflow: Dict[str, Any]) -> Dict[str, Any]:
    return next(
        step for step in workflow["jobs"]["bento"]["steps"] if step.get("id") == "bento"
    )


@pytest.fixture  # type: ignore
def paths() -> Iterator[Paths]:
    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Repo.init(repo_dir, bare=True)
        yield Paths(repo)


@pytest.mark.parametrize(  # type: ignore
    ["workflow_filename", "expected"],
    [["bento.yml", True], ["cant_believe_its_not_bento.yml", False]],
)
def test_is_ci_configured(paths: Paths, workflow_filename: str, expected: bool) -> None:
    paths.workflows_path.mkdir(parents=True)
    (paths.workflows_path / workflow_filename).touch()
    assert uut.is_ci_configured(Context(base_path=paths.repo_path)) is expected


def test_is_ci_configured__no_github_dir(paths: Paths) -> None:
    assert uut.is_ci_configured(Context(base_path=paths.repo_path)) is False


@pytest.mark.parametrize(  # type: ignore
    ["origin_url", "expected"],
    [
        ["git@github.com:returntocorp/bento", True],
        ["https://github.com/returntocorp/bento", True],
        ["https://github-enterprise.returntocorp.com/bento/bento", True],
        ["git@gitlab.com:returntocorp/bento", False],
        ["https://bitbucket.org/returntocorp/bento", False],
    ],
)
def test_is_ci_provider_supported(
    paths: Paths, origin_url: str, expected: bool
) -> None:
    paths.repo.create_remote("origin", origin_url)
    assert uut.is_ci_provider_supported(paths.repo_path) is expected


def test_write_gh_actions_config(paths: Paths) -> None:
    uut._write_gh_actions_config(paths.workflow_path, "ground.control@bento.aero")
    assert paths.workflows_path.exists()
    assert paths.workflow_path.exists()

    workflow = yaml.load(paths.workflow_path.open(), Loader=yaml.SafeLoader)
    assert workflow["name"] == "Bento"
    assert len(workflow["jobs"]) == 1

    bento_step = _bento_step(workflow)
    assert bento_step["with"]["acceptTermsWithEmail"] == "ground.control@bento.aero"


def test_write_gh_actions_config__reinit(paths: Paths) -> None:
    uut._write_gh_actions_config(paths.workflow_path, "ground.control@bento.aero")
    uut._write_gh_actions_config(paths.workflow_path, "food.bank@bento.charity")

    workflow = yaml.load(paths.workflow_path.open(), Loader=yaml.SafeLoader)
    bento_step = _bento_step(workflow)
    assert bento_step["with"]["acceptTermsWithEmail"] == "food.bank@bento.charity"


def test_delete_gh_actions_config(paths: Paths) -> None:
    uut._write_gh_actions_config(paths.workflow_path, "ground.control@bento.aero")
    uut._delete_gh_actions_config(path=paths.workflow_path, root_path=paths.repo_path)
    assert not paths.workflows_path.exists()
    assert not (paths.repo_path / ".github").exists()


def test_delete_gh_actions_config__non_destructive(paths: Paths) -> None:
    sentinel_path = paths.workflows_path / "do_not_remove.yml"
    paths.workflows_path.mkdir(parents=True)
    sentinel_path.touch()

    uut._write_gh_actions_config(paths.workflow_path, "ground.control@bento.aero")
    uut._delete_gh_actions_config(path=paths.workflow_path, root_path=paths.repo_path)
    assert sentinel_path.exists()
