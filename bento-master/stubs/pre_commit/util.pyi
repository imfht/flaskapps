from typing import Any, List, Optional


def noop_context() -> Any:
    ...


def cmd_output(*args: Any, **kwargs: Any) -> str:
    ...


class CalledProcessError(RuntimeError):

    def __init__(self, returncode: int, cmd: List[str], expected_returncode: int, output: Optional[List[str]]=None) -> None:
        self.returncode = returncode
        self.cmd = cmd
        self.expected_returncode = expected_returncode
        self.output = output
        ...

    ...
