from typing import Type

from semantic_version import SimpleSpec

from bento.extra.flake8 import Flake8Parser, Flake8Tool
from bento.parser import Parser
from bento.tool import output

PREFIX = "r2c-flask-"


class FlaskParser(Flake8Parser):
    @staticmethod
    def id_to_link(check_id: str) -> str:
        page = FlaskParser.id_to_name(check_id)
        return f"https://bento.dev/checks/flask/{page}/"

    @classmethod
    def id_to_name(cls, check_id: str) -> str:
        return check_id.replace(PREFIX, "")

    @staticmethod
    def tool() -> Type[output.Str]:
        return FlaskTool


class FlaskTool(Flake8Tool):
    TOOL_ID = "r2c.flask"  # to-do: versioning?
    VENV_DIR = "flask"
    PACKAGES = {
        "flake8": SimpleSpec("~=3.7.0"),
        "flake8-json": SimpleSpec("~=19.8.0"),
        "flake8-flask": SimpleSpec("~=0.9.0"),
    }

    @property
    def parser_type(self) -> Type[Parser]:
        return FlaskParser

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Checks for the Python Flask framework"

    def select_clause(self) -> str:
        return "--select=r2c"
