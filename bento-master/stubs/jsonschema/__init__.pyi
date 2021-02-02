from typing import Any, Callable, Dict


class RefResolutionError(Exception):
    ...


class ValidationError(Exception):
    message: str
    ...


class RefResolver:
    @classmethod
    def from_schema(
        cls, schema: dict, handlers: Dict[str, Callable[[str], Any]]
    ) -> "RefResolver":
        ...


class Draft7Validator:
    def __init__(self, schema: Dict, resolver: RefResolver):
        ...

    def validate(self, json_obj: Dict[str, Any]) -> None:
        ...
