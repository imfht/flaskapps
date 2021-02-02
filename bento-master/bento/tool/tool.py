import logging
import resource
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from time import time
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Pattern,
    Set,
    Type,
    TypeVar,
)

import attr

from bento.base_context import BaseContext
from bento.parser import Parser
from bento.result import from_cache_repr, to_cache_repr
from bento.util import batched
from bento.violation import Violation

R = TypeVar("R")
"""Generic return type"""

JsonR = List[Dict[str, Any]]
"""Return type for tools with a JSON representation"""


MIN_RESERVED_ARGS = 128
"""Number of argument positions reserved for non-file command arguments (e.g. rule ignores)"""


# Note: for now, every tool *HAS* to directly inherit from this, even if it
# also inherits from JsTool or PythonTool. This is so we can list all tools by
# looking at subclasses of Tool.
@attr.s
class Tool(ABC, Generic[R]):
    """The base class for all tool plugins"""

    context = attr.ib(type=BaseContext)

    @property
    def base_path(self) -> Path:
        """Returns the base path from which this tool should run"""
        return self.context.base_path

    @property
    def config(self) -> Dict[str, Any]:
        """Returns this tool's configuration"""
        return self.context.config["tools"][self.tool_id()] or {}

    def parser(self) -> Parser[R]:
        """Returns this tool's parser"""
        return self.parser_type(self.base_path)

    @property
    @abstractmethod
    def parser_type(self) -> Type[Parser[R]]:
        """Returns this tool's parser type"""
        pass

    @classmethod
    @abstractmethod
    def tool_id(cls) -> str:
        """Returns this tool's string ID"""
        pass

    @classmethod
    @abstractmethod
    def tool_desc(cls) -> str:
        """Returns a description of what this tool tests"""
        pass

    @property
    @abstractmethod
    def project_name(self) -> str:
        """Returns this tool's human friendly project name"""
        pass

    @property
    @abstractmethod
    def file_name_filter(self) -> Pattern:
        """Returns a pattern that determines whether a terminal path should be run through this tool"""
        pass

    @property
    def shebang_pattern(self) -> Optional[Pattern]:
        return None

    @abstractmethod
    def setup(self) -> None:
        """
        Runs all code necessary to install this tool

        Code runs inside virtual environment.

        Parameters:
            config (dict): The tool configuration

        Raises:
            CalledProcessError: If setup fails
        """
        pass

    @abstractmethod
    def run(self, files: Iterable[str]) -> R:
        """
        Runs this tool, returning its results

        Code runs inside virtual environment.

        Parameters:
            config (dict): The tool configuration

        Raises:
            CalledProcessError: If execution fails
        """
        pass

    @abstractmethod
    def matches_project(self, files: Iterable[Path]) -> bool:
        """
        Returns true if and only if this project should use this tool
        """
        pass

    def can_use_cache(self) -> bool:
        """
        Returns true if this tool can use cached results

        This should return false if any datum changes that affects caching, other than the file set or the
        Bento version.
        """
        return True

    def extra_cache_paths(self) -> List[Path]:
        """
        Returns extra paths beyond the checked paths whose change should invalidate the cache

        For example, if the tool has a filesystem configuration file, it should be returned here.
        """
        return []

    def project_has_file_paths(self, files: Iterable[Path]) -> bool:
        """
        Returns true iff any unignored files matches at least one extension
        """
        return any(self.filter_paths(files))

    def _file_contains_shebang_pattern(self, file_path: Path) -> bool:
        """
            Checks if the first line of file_path matches self.shebang_pattern.

            Returns False if a "first line" does not make sense for file_path
            i.e. file_path is a binary or is an empty file or doesnt exist
        """
        assert self.shebang_pattern is not None

        if not file_path.is_file():
            # File doesnt exist or is a dir
            return False

        with open(file_path) as file:
            try:
                line: str = next(file)
            except StopIteration:  # Empty file
                return False
            except UnicodeDecodeError:  # Binary file
                return False

        return self.shebang_pattern.match(line) is not None

    def filter_paths(self, paths: Iterable[Path]) -> Set[Path]:
        """
        Filters a list of paths to those that should be analyzed by this tool

        In it's default behavior, this method:
          - Filters terminal paths (files) that match file_name_filter.
          - Filters non-terminal paths (directories) that include at least one matching path.
          - If shebang_pattern is defined filters files that do not match file_name_filter but
            said file's first line matches shebang_pattern

        Parameters:
            paths (list): List of candidate paths

        Returns:
            A set of valid paths
        """
        abspaths = [p.resolve() for p in paths]
        to_run = {
            p
            for p in abspaths
            if self.file_name_filter.match(p.name)
            or (self.shebang_pattern and self._file_contains_shebang_pattern(p))
        }
        return to_run

    def execute(self, command: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        """
        Delegates to subprocess.run() on this tool's base path

        Raises:
            CalledProcessError: If execution fails and check is True
        """
        new_args: Dict[str, Any] = {"cwd": self.base_path, "encoding": "utf8"}
        new_args.update(kwargs)
        cmd_args = (f"'{a}'" for a in command)
        logging.debug(f"{self.tool_id()}: Running: {' '.join(cmd_args)}")
        before = time()
        res = subprocess.run(command, **new_args)
        after = time()
        logging.debug(f"{self.tool_id()}: Command completed in {after - before:2f} s")
        return res

    @classmethod
    def max_batch_size(cls) -> int:
        """Returns the maximum number of files to run in a single batch"""
        # On UNIX, max argc is stack size / 4
        return int(resource.RLIMIT_STACK / 4) - MIN_RESERVED_ARGS

    def _get_findings_from_run(self, paths: Iterable[Path]) -> List[Violation]:
        """
        Returns findings by calling tool "run" method

        :param paths: Paths to run on
        :return:
        """
        paths_to_run = self.filter_paths(paths)
        if not paths_to_run:
            return []

        violations: List[Violation] = []

        for batch in batched(paths_to_run, self.max_batch_size()):
            path_list = [str(p) for p in batch]
            raw = self.run(path_list)
            try:
                violations += self.parser().parse(raw)
            except Exception as e:
                raise Exception(
                    f"Could not parse output of '{self.tool_id()}':\n{raw}", e
                )

        return violations

    def results(self, paths: List[Path], use_cache: bool = True) -> List[Violation]:
        """
        Runs this tool, returning all identified violations

        Code runs inside virtual environment.

        Before running tool, checks local RunCache for cached tool output and skips
        if said output is still usable

        Parameters:
            paths (list or None): If defined, an explicit list of paths to run on
            use_cache (bool): If True, checks for cached results

        Raises:
            CalledProcessError: If execution fails
        """
        if not paths:
            return []

        use_cache = use_cache and self.can_use_cache()

        logging.debug(f"Checking for local cache for {self.tool_id()}")
        cache_repr = self.context.cache.get(
            self.tool_id(), paths + self.extra_cache_paths()
        )
        if not use_cache or cache_repr is None:
            logging.debug(f"Cache entry invalid for {self.tool_id()}. Running Tool.")
            violations = self._get_findings_from_run(paths)
            if use_cache:
                self.context.cache.put(
                    self.tool_id(),
                    paths + self.extra_cache_paths(),
                    to_cache_repr(violations),
                )
        else:
            violations = from_cache_repr(cache_repr)

        ignore_set = set(self.config.get("ignore", []))
        filtered = [v for v in violations if v.check_id not in ignore_set]
        return filtered
