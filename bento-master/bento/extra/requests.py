from typing import Type

from semantic_version import SimpleSpec

from bento.extra.flake8 import Flake8Parser, Flake8Tool
from bento.parser import Parser
from bento.tool import output


class RequestsParser(Flake8Parser):
    CHECK_PREFIX_LEN = len("r2c-requests-")

    @staticmethod
    def id_to_link(check_id: str) -> str:
        return f"https://bento.dev/checks/requests/{check_id}/"

    @classmethod
    def id_to_name(cls, check_id: str) -> str:
        trimmed = check_id[RequestsParser.CHECK_PREFIX_LEN :]
        return trimmed

    @staticmethod
    def tool() -> Type[output.Str]:
        return RequestsTool


class RequestsTool(Flake8Tool):
    TOOL_ID = "r2c.requests"  # to-do: versioning?
    VENV_DIR = "requests"
    PACKAGES = {
        "flake8": SimpleSpec("~=3.7.0"),
        "flake8-json": SimpleSpec("~=19.8.0"),
        "flake8-requests": SimpleSpec("==0.4.0"),
    }

    @property
    def parser_type(self) -> Type[Parser]:
        return RequestsParser

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Checks for the Python Requests framework"

    def select_clause(self) -> str:
        return "--select=r2c"
