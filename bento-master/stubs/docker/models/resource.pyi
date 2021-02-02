class Model:
    # dict.get is used internally so this could technically be -> Optional[str]
    @property
    def id(self) -> str: ...
