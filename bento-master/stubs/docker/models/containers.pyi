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

class ExecResult(NamedTuple):
    exit_code: Optional[int]
    output: Union[bytes, Generator, SocketType, Tuple[bytes, bytes]]

class Container(Model):
    def exec_run(
        self,
        cmd: Union[Iterable[str], str],
        stdout: bool = True,
        stderr: bool = True,
        stdin: bool = False,
        tty: bool = False,
        privileged: bool = False,
        user: str = "",
        detach: bool = False,
        stream: bool = False,
        socket: bool = False,
        environment: Optional[Union[Iterable[str], Mapping[str, str]]] = None,
        workdir: Optional[str] = None,
        demux: bool = False,
    ) -> ExecResult: ...
    def put_archive(self, path: str, data: bytes) -> bool: ...
    def remove(self, **kwargs: Any) -> None: ...
    def start(self, **kwargs: Any) -> None: ...
    def stop(self, **kwargs: Any) -> None: ...

class ContainerCollection:
    def create(
        self,
        image: str,
        command: Optional[Union[str, Iterable[str]]] = None,
        **kwargs: Any
    ) -> Container: ...
    def run(
        self,
        image: str,
        command: Optional[Union[Iterable[str], str]] = None,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs: Any
    ) -> Optional[Union[bytes, Container]]: ...
    def list(
        self,
        all: bool = False,
        before: Optional[str] = None,
        filters: Optional[Mapping[str, Any]] = None,
        limit: int = -1,
        since: Optional[str] = None,
        sparse: bool = False,
        ignore_removed: bool = False,
    ) -> List[Container]: ...
