from typing import Any, Callable, Optional, Union, List

class Metafunc:
    def parametrize(self, name: str, *args: Any, indirect: Union[bool, List[str]]=False, ids: Union[None, List[str], Callable[[str], Optional[str]]]=None, scope: Any=None) -> None:
        ...
