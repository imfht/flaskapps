import time
from pathlib import Path
from unittest.mock import patch

from packaging.version import Version

from bento.cli import _get_latest_version, _get_version_from_cache


def test_nonexistent_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns None if cache file does not exist
    """
    version_cache_path = tmp_path / "version"
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version is None


def test_empty_cache_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns None if version cache is
        empty or is improperly formatted
    """
    version_cache_path = tmp_path / "version"
    version_cache_path.touch()
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version is None


def test_invalid_version_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns None if version cache
        has invalid version string
    """
    version_cache_path = tmp_path / "version"
    version_cache_path.write_text(f"{int(time.time()) - 86500}\ninvalid version string")
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version is None


def test_invalid_timestamp_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns None if timestamp in cache
        is not an int
    """
    version_cache_path = tmp_path / "version"
    version_cache_path.write_text("not an int\n1.1.1")
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version is None


def test_expired_timestamp_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns None if timestamp of cache is
        older than a day (86400000 ns)
    """
    version_cache_path = tmp_path / "version"
    version_cache_path.write_text(f"{int(time.time()) - 86500}\n1.1.1")
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version is None


def test_valid_read_version_cache(tmp_path: Path) -> None:
    """
        Test _get_version_from_cache returns correct value if all is valid
    """
    version_cache_path = tmp_path / "version"
    version_cache_path.write_text(f"{int(time.time()) - 100}\n1.1.2")
    cached_version = _get_version_from_cache(version_cache_path)
    assert cached_version == Version("1.1.2")


def test_get_version_returns_cache(tmp_path: Path) -> None:
    """
        _get_latest_version should return cached version if valid
    """
    with patch("bento.cli._get_version_from_cache") as cache_mock:
        cache_mock.return_value = Version("2.3.4")
        assert _get_latest_version(tmp_path / "version") == Version("2.3.4")


def test_get_version_network_invalid_version(tmp_path: Path) -> None:
    """
        _get_latest_version should return None if network returns invalid version
    """
    with patch("bento.network.fetch_latest_version") as network_mock, patch(
        "bento.cli._get_version_from_cache"
    ) as cache_mock:
        cache_mock.return_value = None
        network_mock.return_value = ("invalid", "invalid")
        version = _get_latest_version(tmp_path / "version")
        assert version is None

        network_mock.return_value = (None, None)
        version = _get_latest_version(tmp_path / "version")
        assert version is None


def test_get_version_network_returns_none(tmp_path: Path) -> None:
    """
        _get_latest_version should return None if network returns None
    """
    with patch("bento.network.fetch_latest_version") as network_mock, patch(
        "bento.cli._get_version_from_cache"
    ) as cache_mock:
        cache_mock.return_value = None
        network_mock.return_value = (None, None)
        version = _get_latest_version(tmp_path / "version")
        assert version is None


def test_read_cache_conforms_with_write(tmp_path: Path) -> None:
    version_path = tmp_path / "version "
    with patch("bento.network.fetch_latest_version") as network_mock, patch(
        "bento.cli._get_version_from_cache"
    ) as cache_mock:
        cache_mock.return_value = None
        network_mock.return_value = ("1.2.5", None)
        version = _get_latest_version(version_path)
        assert version == Version("1.2.5")

    assert _get_version_from_cache(version_path) == Version("1.2.5")
