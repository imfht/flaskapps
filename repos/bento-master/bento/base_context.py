import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Union

import attr
import yaml

import bento.constants as constants
import bento.git
from bento.run_cache import RunCache


def _clean_path(path: Union[str, Path]) -> Path:
    # The resolve here is important, since flake8 seems to have weird behavior
    # regarding finding unused imports if the path is not fully-resolved.
    return Path(path).resolve()


@attr.s
class BaseContext:
    # The path to the directory that contains the .bento dir and .bento.yml
    # file. Tools will also be run from here.
    base_path: Path = attr.ib(converter=_clean_path)
    is_init = attr.ib(type=bool, default=False)
    email = attr.ib(type=Optional[str], default=None)
    cache_path = attr.ib(type=Path, default=None)
    _config = attr.ib(type=Dict[str, Any], default=None)
    _resource_path = attr.ib(type=Path, default=None)
    _cache = attr.ib(type=RunCache, default=None, init=False)
    _ignore_lock = attr.ib(type=Lock, factory=Lock, init=False)

    @base_path.default
    def _find_base_path(self) -> Path:
        """Find the path to the nearest containing directory with bento config.

        This starts at the current directory, then recurses upwards looking for
        a directory with the necessary config file. This function will not recurse
        at or beyond the git project root or the user's home directory.

        If one isn't found, returns the current working directory. This
        behavior is so that you can construct a Context in a directory that
        doesn't have Bento set up, then use the config_path and such to figure
        out where to do the initialization.

        """
        cwd = Path.cwd()

        repo_root = None
        repo_root_obj = bento.git.repo()
        if repo_root_obj is not None:
            repo_root = Path(repo_root_obj.working_tree_dir)

        for base_path in [cwd, *cwd.parents]:
            config_path = base_path / constants.RESOURCE_PATH
            if config_path == constants.GLOBAL_RESOURCE_PATH:  # Don't go past user home
                break
            if (config_path / constants.CONFIG_FILE_NAME).is_file():
                return base_path
            # Stop at root of git repository
            if base_path == repo_root:
                return base_path
        return cwd

    @property
    def config_path(self) -> Path:
        return self.base_path / constants.RESOURCE_PATH / constants.CONFIG_FILE_NAME

    @property
    def resource_path(self) -> Path:
        if not self._resource_path:
            self._resource_path = self.base_path / constants.RESOURCE_PATH
        return self._resource_path

    @property
    def baseline_file_path(self) -> Path:
        return self.resource_path / constants.ARCHIVE_FILE_NAME

    @property
    def ignore_file_path(self) -> Path:
        return self.base_path / constants.IGNORE_FILE_NAME

    @property
    def gh_actions_file_path(self) -> Path:
        return self.base_path / constants.GH_ACTIONS_FILE_NAME

    def pretty_path(self, path: Path) -> Path:
        try:
            return path.relative_to(self.base_path)
        except ValueError:
            return path

    def __attrs_post_init__(self) -> None:
        # We need to make sure the resource directory exists prior to creating the FileIgnore object,
        # otherwise it won't be detected in its directory scan.
        self.resource_path.mkdir(parents=True, exist_ok=True)

    @property
    def config(self) -> Dict[str, Any]:
        if self._config is None:
            self._config = self._open_config()
        return self._config

    @config.setter
    def config(self, config: Dict[str, Any]) -> None:
        self._write_config(config)
        self._config = config

    @property
    def autorun_is_blocking(self) -> bool:
        """
        Returns whether `bento check --staged-only` should block commits
        """
        return self.config.get("autorun", {}).get("block", False)

    @property
    def cache(self) -> RunCache:
        if self._cache is None:
            cp = self.cache_path or (self.resource_path / constants.CACHE_PATH)
            self._cache = RunCache(cache_dir=cp)
        return self._cache

    def _open_config(self) -> Dict[str, Any]:
        """
        Opens this project's configuration file
        """
        logging.info(f"Loading bento configuration from {self.config_path}")
        with self.config_path.open() as yaml_file:
            return yaml.safe_load(yaml_file)

    def _write_config(self, config: Dict[str, Any]) -> None:
        """
        Overwrites this project's configuration file
        """
        logging.info(f"Writing bento configuration to {self.config_path}")
        with self.config_path.open("w") as yaml_file:
            yaml.safe_dump(config, yaml_file)
