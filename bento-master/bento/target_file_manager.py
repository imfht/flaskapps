import logging
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List

import attr
import click
from pre_commit.git import zsplit
from pre_commit.staged_files_only import staged_files_only
from pre_commit.util import CalledProcessError, cmd_output, noop_context

import bento.git
from bento.error import UnsupportedGitStateException
from bento.fignore import FileIgnore, Parser
from bento.tool_runner import RunStep
from bento.util import Colors, echo_error, echo_newline

PATCH_CACHE = str(Path.home() / ".cache" / "bento" / "patches")

GitStatus = namedtuple("GitStatus", ["added", "removed", "unmerged"])


class StatusCode:
    Added = "A"
    Deleted = "D"
    Renamed = "R"
    Unmerged = "U"
    Untracked = "?"
    Ignored = "!"


class NoGitHeadException(Exception):
    """
    Raised by TargetFileManager when trying to get a head context
    and no git head commit is found
    """

    pass


@attr.s
class TargetFileManager:
    """
        Handles all logic related to knowing what files to run on.

        This includes:
            - understanding files are ignores based on bentoignore rules
            - traversing project directories
            - pruning traversal
            - listing staged files
            - changing git state

        Parameters:
            base_path: Path to start walking files from
            paths: List of Paths (absolute or relative to current working directory) that
                    we want to traverse
            staged: whether we want to scan just staged files
            ignore_rules_file_path: Path to .bentoignore file
    """

    _base_path = attr.ib(type=Path)
    _paths = attr.ib(type=List[Path])
    _staged = attr.ib(type=bool)
    _ignore_rules_file_path = attr.ib(type=Path)
    _target_paths = attr.ib(type=List[Path], init=False)

    def _staged_paths(self) -> List[Path]:
        """
            Returns Absolute Paths to all files that are staged
        """
        repo = bento.git.repo()
        if not repo:
            return []

        # Output of git command will be relative to git project root
        cmd = [
            "git",
            "diff",
            "--name-only",
            "--no-ext-diff",
            "-z",
            # Everything except for D
            "--diff-filter=ACMRTUXB",
            "--staged",
        ]
        result = repo.git.execute(cmd)
        str_paths = zsplit(result)

        # Resolve paths relative to git project root
        return [(Path(repo.working_tree_dir) / p).resolve() for p in str_paths]

    @_target_paths.default
    def _get_target_files(self) -> List[Path]:
        """
            Return list of all absolute paths to analyze
        """
        # resolve given paths relative to current working directory
        paths = [p.resolve() for p in self._paths]

        # If staged then only run on files that are different
        # and are a subpath of anything in input_paths
        if self._staged:
            targets = self._staged_paths()
            paths = [
                diff_path
                for diff_path in targets
                # diff_path is a subpath of some element of input_paths
                if any(
                    (diff_path == path or path in diff_path.parents) for path in paths
                )
            ]

        # Filter out ignore rules, expand directories
        with self._ignore_rules_file_path.open() as ignore_lines:
            patterns = Parser(self._base_path, self._ignore_rules_file_path).parse(
                ignore_lines
            )

        file_ignore = FileIgnore(
            base_path=self._base_path, patterns=patterns, target_paths=paths
        )

        filtered: List[Path] = []
        for elem in file_ignore.entries():
            if elem.survives:
                filtered.append(elem.path)

        return filtered

    def _git_status(self) -> GitStatus:
        """
            Gets added, removed, and unmerged paths from the git index
        """
        status_output = (
            cmd_output("git", "status", "--porcelain", "-z")[1].rstrip().split("\0")
        )
        next_is_file = False
        added = []
        removed = []
        unmerged = []
        for s in status_output:
            if not s.strip():
                continue
            if next_is_file:
                # We are in source line of rename
                next_is_file = False
                removed.append(s)
                continue
            if s[0] == StatusCode.Untracked or s[0] == StatusCode.Ignored:
                continue

            fname = s[3:]
            # The following detection for unmerged codes comes from `man git-status`
            if (
                s[0] == StatusCode.Added
                and s[1] == StatusCode.Added
                or s[0] == StatusCode.Deleted
                and s[1] == StatusCode.Deleted
                or s[0] == StatusCode.Unmerged
                or s[1] == StatusCode.Unmerged
            ):
                unmerged.append(fname)
            if s[0] == StatusCode.Renamed:
                added.append(fname)
                next_is_file = True
            if s[0] == StatusCode.Added:
                added.append(fname)
            if s[0] == StatusCode.Deleted:
                removed.append(fname)
        logging.info(
            f"Git status:\nadded: {added}\nremoved: {removed}\nunmerged: {unmerged}"
        )
        return GitStatus(added, removed, unmerged)

    def _abort_if_untracked_and_removed(self, removed: List[str]) -> None:
        """
            Raises UnsupportedGitStateException if any path is removed from
            the git index but also appears in the filesystem.

            :param removed (list): Removed paths
            :raises UnsupportedGitStateException: If any removed paths are present on Filesystem
        """
        untracked_removed = [r.replace(" ", r"\ ") for r in removed if Path(r).exists()]
        if untracked_removed:
            joined = " ".join(untracked_removed)

            def echo_cmd(cmd: str) -> None:
                click.echo(f"    $ {click.style(cmd, bold=True)}\n", err=True)

            echo_error(
                "One or more files deleted from git exist on the filesystem. Aborting to prevent data loss. To "
                "continue, please stash by running the following two commands:"
            )
            echo_newline()
            echo_cmd(f"git stash -u -- {joined}")
            echo_cmd(f"git rm {joined}")
            click.secho(
                "Stashed changes can later be recovered by running:\n",
                err=True,
                fg=Colors.ERROR,
            )
            echo_cmd(f"git stash pop")
            raise UnsupportedGitStateException()

    @contextmanager
    def _head_context(self) -> Iterator[None]:
        """
        Runs a block of code on files from the current branch HEAD.

        :raises subprocess.CalledProcessError: If git encounters an exception
        :raises NoGitHeadException: If git cannot detect a HEAD commit
        :raises UnsupportedGitStateException: If unmerged files are detected
        """
        repo = bento.git.repo()

        if not repo:
            yield
            return

        commit = bento.git.commit()
        if commit is None:
            raise NoGitHeadException()

        else:
            added, removed, unmerged = self._git_status()

            # Need to look for unmerged files first, otherwise staged_files_only will eat them
            if unmerged:
                echo_error(
                    "Please resolve merge conflicts in these files before continuing:"
                )
                for f in unmerged:
                    click.secho(f, err=True)
                raise UnsupportedGitStateException()

            with staged_files_only(PATCH_CACHE):
                tree = cmd_output("git", "write-tree")[1].strip()
                self._abort_if_untracked_and_removed(removed)
                try:
                    for a in added:
                        (repo.working_tree_dir / Path(a)).unlink()
                    cmd_output("git", "checkout", "HEAD", "--", ".")
                    yield
                finally:
                    # git checkout will fail if the checked-out index deletes all files in the repo
                    # In this case, we still want to continue without error.
                    # Note that we have no good way of detecting this issue without inspecting the checkout output
                    # message, which means we are fragile with respect to git version here.
                    try:
                        cmd_output("git", "checkout", tree.strip(), "--", ".")
                    except CalledProcessError as ex:
                        if (
                            ex.output
                            and len(ex.output) >= 2
                            and "pathspec '.' did not match any file(s) known to git"
                            in ex.output[1].strip()
                        ):
                            logging.warning(
                                "Restoring git index failed due to total repository deletion; skipping checkout"
                            )
                        else:
                            raise ex
                    if removed:
                        cmd_output("git", "rm", *removed)

    @contextmanager
    def run_context(self, staged: bool, run_step: RunStep) -> Iterator[List[Path]]:
        """
        Provides a context within which to run tools and returns list of paths
        that should be analyzed.

        Possible contexts include:

            Head Context: all files in current branch HEAD
            Staged Files Context: all files in current branch HEAD plus staged changes
                                  (hides all untracked files)
            Noop: all files as currently available on filesystem

        Returned list of paths are all abolute paths and include all files that are
            - not ignored based on .bentoignore rules and
            - exist in any path filters specified.

        :param staged: Whether to use remove file diffs
        :param run_step: Which run step is in use (baseline if tool is determining baseline, check if tool is finding new results)
        :return: A Python with-expression
        :raises subprocess.CalledProcessError: If git encounters an exception
        :raises NoGitHeadException: If git cannot detect a HEAD commit
        :raises UnsupportedGitStateException: If unmerged files are detected
        """
        if staged and run_step == RunStep.BASELINE:
            stash_context = self._head_context()
        elif staged:
            stash_context = staged_files_only(PATCH_CACHE)
        else:
            # staged is False
            stash_context = noop_context()

        with stash_context:
            yield self._target_paths
