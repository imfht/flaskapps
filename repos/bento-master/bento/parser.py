import os
from pathlib import Path
from typing import Generic, List, TypeVar

import attr

from bento.violation import Violation

R = TypeVar("R", contravariant=True)


def _absolute(path: Path) -> Path:
    return path.absolute()


@attr.s
class Parser(Generic[R]):
    base_path = attr.ib(type=Path, converter=_absolute)

    def trim_base(self, path: str) -> str:
        wrapped = Path(path)
        if not wrapped.is_absolute():
            wrapped = self.base_path / wrapped
        return os.path.relpath(wrapped, self.base_path)

    def parse(self, result: R) -> List[Violation]:
        return []
