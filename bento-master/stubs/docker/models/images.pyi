from socket import SocketType
from typing import (
    Any,
    Generator,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

from .resource import Model

class Image(Model):
    @property
    def tags(self) -> List[str]: ...

class ImageCollection:
    def list(
        self,
        name: Optional[str] = None,
        all: bool = False,
        filters: Optional[Mapping[str, Any]] = None,
    ) -> List[Image]: ...
    def pull(self, platform: Optional[str] = None) -> Image: ...
