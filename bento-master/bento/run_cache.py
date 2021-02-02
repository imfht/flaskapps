import json
import logging
from pathlib import Path
from typing import Iterable, Optional

import attr
import pymmh3 as mmh3

from bento import __version__ as BENTO_VERSION


@attr.s
class RunCache:
    """
        Acts as a local cache for tool run output

        Different tools can be accessed concurrently, but cache access
        is not threadsafe if multiple threads access the same tool.
    """

    cache_dir: Path = attr.ib(converter=Path)

    def __cache_metadata_path(self, tool_id: str) -> Path:
        """
            Returns name of file that cache results metadata for a given tool
        """
        return self.cache_dir / f"{tool_id}-meta.json"

    def __cache_data_path(self, tool_id: str) -> Path:
        """
            Returns name of file that cache results would be contained in
        """
        return self.cache_dir / f"{tool_id}.data"

    def _modified_hash(self, paths: Iterable[Path]) -> str:
        """
        Returns a hash of the recursive mtime of a path.

        Any modification of a file within this tree (that does not match an ignore pattern)
        will change the hash.
        """

        # No matter settings of .bentoignore, these are always excluded
        files_and_times = ((str(p), p.stat().st_mtime_ns) for p in paths if p.exists())
        h = 0
        for f, m in files_and_times:
            h ^= mmh3.hash128(f"{f}:{m}")

        return format(h, "x")

    def __cleanup(self, tool_id: str) -> None:
        """
            Delete all state relevant for cacheing tool_id
        """
        cache_metadata_path = self.__cache_metadata_path(tool_id)
        cache_data_path = self.__cache_data_path(tool_id)

        # Silently delete file if exists
        # note that checking for file before deletion
        # has a TOCTOU race so will need a try-catch anyway
        try:
            cache_metadata_path.unlink()
        except OSError:
            pass

        try:
            cache_data_path.unlink()
        except OSError:
            pass

    def wipe(self) -> None:
        try:
            self.cache_dir.unlink()
        except OSError:
            pass

    def get(self, tool_id: str, paths: Iterable[Path]) -> Optional[str]:
        """
            Returns stored run output if it exists in local run cache and the
            cache entry is still valid (files have not been modified since caching)

            Returns None if no such cache entry is found
        """
        cache_metadata_path = self.__cache_metadata_path(tool_id)
        cache_data_path = self.__cache_data_path(tool_id)

        if not (cache_metadata_path.exists() and cache_data_path.exists()):
            self.__cleanup(tool_id)
            return None

        with cache_metadata_path.open() as file:
            try:
                metadata = json.load(file)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse tool {tool_id} cache metadata as json")
                logging.error(e.msg, e.doc, e.pos)
                self.__cleanup(tool_id)
                return None

        cache_hash = metadata.get("hash")
        cache_paths = {Path(p) for p in metadata.get("paths")}
        cache_bento_version = metadata.get("version")

        if (
            cache_paths != set(paths)
            or cache_bento_version != BENTO_VERSION
            or cache_hash != self._modified_hash(paths)
        ):
            logging.warning(f"Invalidating cache for {tool_id}")
            self.__cleanup(tool_id)
            return None

        return cache_data_path.read_text()

    def put(self, tool_id: str, paths: Iterable[Path], raw_results: str) -> None:
        """
            Caches raw_results as the output of running TOOL_ID on PATHS

            Note that RunCache.get assumed paths is not None so should be changed
            if PATHS here is nullable
        """
        self.__cleanup(tool_id)

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_metadata_path = self.__cache_metadata_path(tool_id)
        cache_data_path = self.__cache_data_path(tool_id)

        # Data should be written before metadata
        cache_data_path.write_text(raw_results)
        hsh = self._modified_hash(paths)

        metadata = {
            "paths": [str(p) for p in paths],
            "hash": hsh,
            "version": BENTO_VERSION,
        }

        with cache_metadata_path.open("w") as file:
            json.dump(metadata, file)
