from typing import List

class Process():

    def parents(self) -> List[Process]:
        ...

    def name(self) -> str:
        ...
