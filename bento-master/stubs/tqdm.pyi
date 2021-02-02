from typing import Any, Iterable, Optional

class tqdm:
    def __init__(
        self,
        iterable: Optional[Iterable[Any]]=None,
        desc: Optional[str]=None,
        total: Optional[float]=None,
        leave: bool =True,
        file: Optional[str]=None,
        ncols: Optional[int]=None,
        mininterval: float=0.1,
        maxinterval: float=10.0,
        miniters: Optional[float]=None,
        ascii: Optional[str] =None,
        disable: bool=False,
        unit: str="it",
        unit_scale: bool=False,
        dynamic_ncols: bool=False,
        smoothing: float=0.3,
        bar_format: Optional[str]=None,
        initial: int=0,
        position: Optional[int]=None,
        postfix: Optional[str]=None,
        unit_divisor: int=1000,
    ) -> None:
        self.n: int = ...
        ...
    def update(self, n: int = 1) -> None: ...
    def close(self) -> None: ...
    def set_postfix_str(self, text: str) -> None: ...
