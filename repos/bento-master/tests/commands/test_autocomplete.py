import os
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from typing import Iterator, Optional
from unittest.mock import patch

from click.testing import CliRunner

from bento.commands.autocomplete import install_autocomplete, uninstall_autocomplete


@contextmanager
def _fake_rc(
    tmp_path: Path, name: str, shell: Optional[str], create: bool = True
) -> Iterator[Path]:
    profile_path = tmp_path / name
    if create:
        with profile_path.open("w") as stream:
            stream.write("# This is a fake rc file\n")
    with patch("pathlib.Path.home", lambda: tmp_path):
        memo = os.environ.get("SHELL")
        try:
            if shell:
                os.environ["SHELL"] = shell
            elif memo:
                del os.environ["SHELL"]
            yield profile_path
        finally:
            if memo:
                os.environ["SHELL"] = memo
            elif shell:
                del os.environ["SHELL"]


def test_enable_adds_to_bashrc(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".bashrc", "/bin/bash") as profile_path:
        runner.invoke(install_autocomplete)
        with profile_path.open() as stream:
            content = stream.read()

    expectation = dedent(
        """
        # This is a fake rc file

        eval "$(_BENTO_COMPLETE=source bento)"
        """
    ).lstrip()

    assert content == expectation


def test_enable_adds_to_zshrc(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".zshrc", "/bin/zsh") as profile_path:
        runner.invoke(install_autocomplete)
        with profile_path.open() as stream:
            content = stream.read()

    expectation = dedent(
        """
        # This is a fake rc file

        eval "$(_BENTO_COMPLETE=source_zsh bento)"
        """
    ).lstrip()

    assert content == expectation


def test_enable_errors_if_no_shell(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".fishrc", None):
        result = runner.invoke(install_autocomplete)
        assert result.exit_code == 1


def test_enable_errors_if_unknown_shell(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".fishrc", "/bin/fish"):
        result = runner.invoke(install_autocomplete)
        assert result.exit_code == 1


def test_enable_creates_profile(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".bashrc", "/bin/bash", create=False) as profile_path:
        assert not profile_path.exists()
        runner.invoke(install_autocomplete)
        assert profile_path.exists()


def test_disable_removes_autocomplete_bash(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".bashrc", "/bin/bash") as profile_path:
        runner.invoke(install_autocomplete)
        runner.invoke(uninstall_autocomplete)
        with profile_path.open() as stream:
            content = stream.read()

    expectation = dedent(
        """
        # This is a fake rc file

        """
    ).lstrip()

    assert content == expectation


def test_disable_removes_autocomplete_zsh(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".zshrc", "/bin/zsh") as profile_path:
        runner.invoke(install_autocomplete)
        runner.invoke(uninstall_autocomplete)
        with profile_path.open() as stream:
            content = stream.read()

    expectation = dedent(
        """
        # This is a fake rc file

        """
    ).lstrip()

    assert content == expectation


def test_disable_succeeds_no_autocomplete(tmp_path: Path) -> None:
    runner = CliRunner(mix_stderr=False)

    with _fake_rc(tmp_path, ".bashrc", "/bin/bash") as profile_path:
        runner.invoke(uninstall_autocomplete)
        with profile_path.open() as stream:
            content = stream.read()

    expectation = dedent(
        """
        # This is a fake rc file
        """
    ).lstrip()

    assert content == expectation
