import io
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import click

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from bento.cli import cli
from bento.commands.register import Registrar
from bento.constants import QA_TEST_EMAIL_ADDRESS, TERMS_OF_SERVICE_VERSION
from bento.context import Context
from bento.error import NonInteractiveTerminalException
from bento.util import persist_global_config, read_global_config

INTEGRATION = Path(__file__).parent.parent / "integration"


@contextmanager
def tmp_config(tmp_path: Path) -> Iterator[click.Context]:
    click_context = click.Context(cli)
    context = Context(base_path=INTEGRATION / "simple")
    context.is_init = True
    click_context.obj = context

    memo = os.environ.get("SHELL")
    with patch("bento.constants.GLOBAL_CONFIG_PATH", tmp_path / "config.yml"):
        try:
            if memo:
                del os.environ["SHELL"]
            yield (click_context)
        finally:
            if memo:
                os.environ["SHELL"] = memo


@contextmanager
def fake_input(tmp_path: Path, input: str) -> Iterator[click.Context]:
    stdin = io.StringIO(input)
    with patch.object(stdin, "isatty", lambda: True):
        with patch("sys.stdin", stdin):
            with patch.object(sys.stderr, "isatty", lambda: True):
                with tmp_config(tmp_path) as ctx:
                    yield (ctx)


@contextmanager
def setup_global_gitignore(tmp_path: Path) -> Iterator[None]:
    tmp_ignore = tmp_path / ".gitignore"
    with tmp_ignore.open("w") as stream:
        stream.write(".bento/\n")
    with patch("bento.git.global_ignore_path", lambda p: tmp_ignore):
        yield


def test_register_email_from_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BENTO_EMAIL", "heresjohnny@r2c.dev")

    ctx = click.Context(cli)
    context = Context(base_path=INTEGRATION / "simple")
    context.is_init = True
    ctx.obj = context

    registrar = Registrar(click_context=ctx, agree=False)

    assert registrar.email == "heresjohnny@r2c.dev"


def test_register_noninteractive(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Asserts error is raised when registering with noninteractive terminal"""
    expectation = """
╭──────────────────────────────────────────────────────────────────────────────╮
│                          Global Bento Configuration                          │
╰──────────────────────────────────────────────────────────────────────────────╯
Thanks for installing Bento, a free and opinionated toolkit for gradually
adopting linters and program analysis in your codebase!

Registration: We’ll use your email to provide support and share product
updates. You can unsubscribe at any time.

✘ This installation of Bento is not registered.

Please either:
◦ Register Bento by running it in an interactive terminal
◦ Run Bento with `--agree --email [EMAIL]`
"""

    with tmp_config(tmp_path) as ctx:
        registrar = Registrar(click_context=ctx, agree=False, email=None)

        with pytest.raises(NonInteractiveTerminalException) as ex:
            registrar.verify()

        assert ex.value.code == 3

    outerr = capsys.readouterr()
    assert outerr.err == expectation
    assert not outerr.out


def test_register_agree_email(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Asserts registration is skipped with both email and agree"""
    with tmp_config(tmp_path) as ctx:
        registrar = Registrar(
            click_context=ctx, agree=True, email=QA_TEST_EMAIL_ADDRESS
        )

        assert registrar.verify()

    outerr = capsys.readouterr()
    assert not outerr.err
    assert not outerr.out


def test_register_happy_path(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Asserts registration succeeds when sending email and agreeing to ToS"""

    email_question = "What is your email address?"
    tos_question = "Continue and agree to Bento's terms of service and privacy policy?"

    with setup_global_gitignore(tmp_path):
        with fake_input(tmp_path, f"{QA_TEST_EMAIL_ADDRESS}\n\n") as ctx:
            registrar = Registrar(click_context=ctx, agree=False, email=None)

            assert registrar.verify()
            assert read_global_config() == {
                "email": QA_TEST_EMAIL_ADDRESS,
                "terms_of_service": "0.3.0",
            }

    outerr = capsys.readouterr()
    assert email_question in outerr.err
    assert tos_question in outerr.err
    assert not outerr.out


def test_already_registered(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Asserts registration skipped if current"""

    with setup_global_gitignore(tmp_path):
        with tmp_config(tmp_path) as ctx:
            persist_global_config(
                {
                    "email": QA_TEST_EMAIL_ADDRESS,
                    "terms_of_service": TERMS_OF_SERVICE_VERSION,
                }
            )
            registrar = Registrar(
                click_context=ctx, agree=False, email=QA_TEST_EMAIL_ADDRESS
            )
            assert registrar.verify()

    output = capsys.readouterr()
    assert not output.err
    assert not output.out


def test_register_email_option(tmp_path: Path) -> None:
    """Validates registration if email via command line"""

    with setup_global_gitignore(tmp_path):
        with fake_input(tmp_path, "\n") as ctx:
            registrar = Registrar(
                click_context=ctx, agree=False, email=QA_TEST_EMAIL_ADDRESS
            )

            assert registrar.verify()
            assert read_global_config() == {
                "terms_of_service": TERMS_OF_SERVICE_VERSION
            }


def test_register_setup_gitignore(tmp_path: Path) -> None:
    """Validates that registration configures global gitignore"""

    tmp_ignore = tmp_path / ".gitignore"
    with patch("bento.git.global_ignore_path", lambda p: tmp_ignore):
        with fake_input(tmp_path, "\n\n") as ctx:
            registrar = Registrar(
                click_context=ctx, agree=False, email=QA_TEST_EMAIL_ADDRESS
            )
            assert registrar.verify()

        with tmp_ignore.open("r") as stream:
            lines = [l.rstrip() for l in stream]

        assert ".bento/" in lines
        assert ".bentoignore" in lines


def test_register_agree_flag(tmp_path: Path) -> None:
    """Validates registration if agreement in flag"""

    with fake_input(tmp_path, f"{QA_TEST_EMAIL_ADDRESS}\n\n") as ctx:
        registrar = Registrar(click_context=ctx, agree=True, email=None)

        assert registrar.verify()
        assert read_global_config() == {"email": QA_TEST_EMAIL_ADDRESS}


def test_register_no_agree(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Asserts registration fails when rejecting ToS"""

    expectation = """✘ Bento did NOT install. Bento beta users must agree to the terms of service to
continue. Please reach out to us at support@r2c.dev with questions or concerns."""

    with fake_input(tmp_path, f"{QA_TEST_EMAIL_ADDRESS}\nn\n") as ctx:
        registrar = Registrar(click_context=ctx, agree=False, email=None)

        assert not registrar.verify()
        assert read_global_config() == {"email": QA_TEST_EMAIL_ADDRESS}

    output = capsys.readouterr()
    assert expectation in output.err
    assert not output.out
