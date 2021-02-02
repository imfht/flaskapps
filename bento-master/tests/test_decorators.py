import contextlib
import sys
from typing import Any, Iterator, List

import click

import bento.network
from _pytest.monkeypatch import MonkeyPatch
from bento.decorators import with_metrics
from bento.network import PostData


def _mock_post_metrics(
    monkeypatch: MonkeyPatch, shouldPass: bool = True
) -> List[PostData]:
    posted: List[Any] = []

    def mock_post_metrics(data: PostData) -> bool:
        posted.append(data)
        return shouldPass

    monkeypatch.setattr(bento.network, "post_metrics", mock_post_metrics)
    return posted


@contextlib.contextmanager
def _command(name: str) -> Iterator[click.Context]:
    cmd = click.Command(name)
    context = click.Context(cmd)
    try:
        click.globals.push_context(context)
        yield context
    finally:
        click.globals.pop_context()


def test_sends_metrics_no_failures(monkeypatch: MonkeyPatch) -> None:
    posted = _mock_post_metrics(monkeypatch)
    with _command("test"):
        with_metrics(lambda: ())()
    assert len(posted) == 1
    assert posted[0][0]["command"] == "test"
    assert posted[0][0]["exit_code"] == 0
    assert "exception" not in posted[0][0]


def test_sends_metrics_sys_exit(monkeypatch: MonkeyPatch) -> None:
    posted = _mock_post_metrics(monkeypatch)
    with _command("test"):
        try:
            with_metrics(lambda: sys.exit(123))()
        except SystemExit as ex:
            assert ex.code == 123
    assert len(posted) == 1
    assert posted[0][0]["command"] == "test"
    assert posted[0][0]["exit_code"] == 123
    assert "exception" not in posted[0][0]


def test_sends_metrics_exception(monkeypatch: MonkeyPatch) -> None:
    def say_hi() -> None:
        raise Exception("hi")

    posted = _mock_post_metrics(monkeypatch)
    with _command("test"):
        try:
            with_metrics(say_hi)()
        except Exception as ex:
            assert str(ex) == "hi"
    assert len(posted) == 1
    assert posted[0][0]["command"] == "test"
    assert posted[0][0]["exit_code"] == 3
    # TODO add back test for "exception" once we have better exception types or messages without PII
