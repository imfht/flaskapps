import os
import tempfile
import time
from pathlib import Path
from typing import Tuple

from _pytest.monkeypatch import MonkeyPatch
from bento.run_cache import RunCache

TOOL_ID = "tool_name_here"
TOOL_OUTPUT = "this is tool output"
THIS_PATH = os.path.dirname(__file__)


def __ensure_ubuntu_mtime_change() -> None:
    """
    On Ubuntu, file mtimes are not updated if a small enough time has passed.

    To ensure mtime change, sleep at least 10 ms.
    """
    time.sleep(1e-2)


def __hash(tmp_file: Path) -> str:
    with tempfile.TemporaryDirectory() as cache_dir:
        return RunCache(cache_dir)._modified_hash([tmp_file])


def __setup_test_dir(
    tmp_path: Path, subdir_name: str = "subdir", touch_file: bool = True
) -> Tuple[str, Path]:
    subdir = tmp_path / subdir_name
    subdir.mkdir()
    file = subdir / "hello.txt"
    if touch_file:
        file.touch()
    hsh = __hash(file)
    return hsh, file


def test_modified_hash_no_changes(tmp_path: Path) -> None:
    """modified_hash should not change if no files change"""

    hsh, file = __setup_test_dir(tmp_path)
    __ensure_ubuntu_mtime_change()

    assert hsh == __hash(file)


def test_modified_hash_new_file_subdir(tmp_path: Path) -> None:
    """modified_hash should change if a new file in subdir is added"""
    hsh, file = __setup_test_dir(tmp_path, touch_file=False)

    file.touch()

    assert hsh != __hash(file)


def test_modified_hash_touch(tmp_path: Path) -> None:
    """modified_hash should change if a file is modified"""

    hsh, file = __setup_test_dir(tmp_path)
    __ensure_ubuntu_mtime_change()
    file.touch()

    assert hsh != __hash(file)


def test_modified_hash_remove(tmp_path: Path) -> None:
    """modified_hash should change if a file is removed"""

    hsh, file = __setup_test_dir(tmp_path)
    file.unlink()

    assert hsh != __hash(file)


def test_get(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    _, file = __setup_test_dir(tmp_path)

    paths = [file]

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = Path(tmpdir)

        # Check cache is retrievable
        cache = RunCache(cache_path)
        assert cache.get(TOOL_ID, paths) is None
        cache.put(TOOL_ID, paths, TOOL_OUTPUT)

        cache = RunCache(cache_path)
        assert cache.get(TOOL_ID, paths) == TOOL_OUTPUT

        # Check that modifying file invalidates cache
        __ensure_ubuntu_mtime_change()
        file.touch()

        cache = RunCache(cache_path)
        assert cache.get(TOOL_ID, paths) is None
