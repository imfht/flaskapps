import io
import os
from pathlib import Path
from typing import Collection, Set

import pytest
from _pytest.monkeypatch import MonkeyPatch
from bento.fignore import FileIgnore, Parser, Processor, open_ignores

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = (THIS_PATH / "..").resolve()
WALK_PATH = (BASE_PATH / "tests/integration/simple").relative_to(Path(os.getcwd()))


def __kept(ignores: Set[str]) -> Collection[Path]:
    fi = FileIgnore(WALK_PATH, ignores, [WALK_PATH])
    return {e.path for e in fi.entries() if e.survives}


def test_no_ignore() -> None:
    all_files = __kept(set())
    assert WALK_PATH / ".bento" / "config.yml" in all_files
    assert WALK_PATH / ".bento" / "archive.json" in all_files


def test_ignore_any_dir() -> None:
    all_files = __kept({"dist/", "node_modules/", ".bento/"})
    assert WALK_PATH / "dist/init.min.js" not in all_files


def test_ignore_any_file() -> None:
    all_files = __kept({".bento.yml"})
    assert WALK_PATH / ".bento.yml" not in all_files


def test_ignore_root_file_exists() -> None:
    all_files = __kept({"/init.js"})
    assert WALK_PATH / "init.js" not in all_files


def test_ignore_root_file_not_exists() -> None:
    all_files = __kept({"/bar.js"})
    assert WALK_PATH / "dist" / "foo" / "bar.js" in all_files


def test_ignore_relative_file_exists() -> None:
    all_files = __kept({"./init.js"})
    assert WALK_PATH / "init.js" not in all_files


def test_ignore_relative_dot_file_exists() -> None:
    all_files = __kept({"./.bento/"})
    assert WALK_PATH / ".bento" not in all_files


def test_ignore_relative_file_not_exists() -> None:
    all_files = __kept({"./bar.js"})
    assert WALK_PATH / "dist" / "foo" / "bar.js" in all_files


def test_ignore_not_nested() -> None:
    all_files = __kept({"foo/bar.js", ".bento/"})
    assert WALK_PATH / "dist/foo/bar.js" in all_files


def test_ignore_nested_terminal_syntax() -> None:
    all_files = __kept({"foo/", ".bento/", "node_modules/"})
    assert WALK_PATH / "dist/foo/bar.js" not in all_files


def test_ignore_nested_double_start_syntax() -> None:
    all_files = __kept({"**/foo/", ".bento/"})
    assert WALK_PATH / "dist/foo/bar.js" not in all_files


def test_ignore_full_path() -> None:
    all_files = __kept({"dist/foo/bar.js"})
    assert WALK_PATH / "dist/foo/bar.js" not in all_files


def __parse(text: str, base_path: Path = BASE_PATH) -> Set[str]:
    lines = io.StringIO(text)
    parser = Parser(base_path, Path("test"))
    return parser.parse(lines)


def test_load_includes(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.chdir(BASE_PATH)

    assert "node_modules/" in __parse(":include .gitignore")


def test_load_includes_from_path(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.chdir(BASE_PATH)

    assert "node_modules/" in __parse(":include ../.gitignore", BASE_PATH / "tests")


def test_load_escape_colon() -> None:
    assert r"\:foo" in __parse(r"\:foo")


def test_escape_random_character() -> None:
    processor = Processor(BASE_PATH)
    assert r"**/#" in processor.process([r"\#"])


def test_include_emacs_swap() -> None:
    assert r"*#" in __parse(r"*#")


def test_strip_comments() -> None:
    assert "foo" in __parse(r"foo # this is a comment")


def test_comment_line() -> None:
    assert not __parse(r"# this is a comment at the start of the line")


def test_load_git_include() -> None:
    assert not __parse(r"!foo")


def test_load_git_multi_char() -> None:
    assert not __parse(r"*.py[cod]")


def test_load_unknown_command() -> None:
    with pytest.raises(ValueError) as ex:
        __parse(":unknown")
    assert ex


def test_ignores_from_ignore_file(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.chdir(BASE_PATH)

    test_path = Path("tests") / "integration" / "simple"
    (test_path / ".bento").mkdir(exist_ok=True)
    (test_path / "node_modules").mkdir(exist_ok=True)

    fi = open_ignores(test_path, BASE_PATH / ".bentoignore")
    print(fi.patterns)

    survivors = {str(e.path) for e in fi.entries() if e.survives}
    assert survivors == {
        "tests/integration/simple/.bentoignore",
        "tests/integration/simple/init.js",
        "tests/integration/simple/package-lock.json",
        "tests/integration/simple/package.json",
        "tests/integration/simple/bar.py",
        "tests/integration/simple/foo.py",
        "tests/integration/simple/baz.py",
        "tests/integration/simple/jinja-template.html",
    }

    rejects = {str(e.path) for e in fi.entries() if not e.survives}
    assert rejects == {
        "tests/integration/simple/.bento",
        "tests/integration/simple/.gitignore",
        "tests/integration/simple/dist",
        "tests/integration/simple/node_modules",
    }
