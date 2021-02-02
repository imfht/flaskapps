import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Pattern, Type

from bento.parser import Parser
from bento.tool import output
from bento.util import fetch_line_in_file
from bento.violation import Violation

# Input example:
# { "line": 49,
# "column": 49,
# "path": "tests/test_tool.py",
# "code": 11,
# "name": "Undefined type",
# "description": "Undefined type [11]: Type `Iterable` is not defined.",
# "long_description": "Undefined type [11]: Type `Iterable` is not defined.",
# "concise_description": "Undefined type [11]: Type `Iterable` is not defined.",
# "inference": {},
# "ignore_error": false,
# "external_to_global_root": false
# }

PINNED_PYRE_VERSION = "0.0.32"


class PyreParser(Parser):
    def to_violation(self, result: Dict[str, Any]) -> Violation:
        path = self.trim_base(result["path"])
        abspath = self.base_path / path

        check_id = str(result["code"])
        line = result["line"]
        return Violation(
            tool_id=PyreTool.TOOL_ID,
            check_id=check_id,
            path=path,
            line=line,
            column=result["column"],
            message=result["description"],
            severity=2,
            syntactic_context=fetch_line_in_file(abspath, line) or "<no source found>",
            link="https://pyre-check.org/docs/error-types.html",
        )

    def parse(self, tool_output: str) -> List[Violation]:
        results: List[Dict[str, Any]] = json.loads(tool_output)
        return [self.to_violation(r) for r in results]


class PyreTool(output.Str):
    TOOL_ID = "pyre"  # to-do: versioning?
    PROJECT_NAME = "Python"

    @property
    def parser_type(self) -> Type[Parser]:
        return PyreParser

    @classmethod
    def tool_id(self) -> str:
        return PyreTool.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Finds type errors in Python code"

    @property
    def project_name(self) -> str:
        return PyreTool.PROJECT_NAME

    @property
    def file_name_filter(self) -> Pattern:
        return re.compile(r".*\.py\b")

    def matches_project(self, files: Iterable[Path]) -> bool:
        # disabled by default for now
        return False

    def setup(self) -> None:
        cmd = ["pip3", "install", "-q", f"pyre-check=={PINNED_PYRE_VERSION}"]
        self.execute(cmd)

    def run(self, files: Iterable[str]) -> str:
        # for pyre, we also want to make sure that we are running in the same venv environment that the
        # source project is in, so that all the dependencies and types are resolvable
        if not os.environ.get("PIPENV_ACTIVE") == "1":
            raise Exception(
                "pyre requires being run from this project's pipenv, but no pipenv is active"
            )

        # TODO: we haven't verified that we're in the *right* pipenv, just that we're in *a* pipenv
        # TODO: may need to do this *in parallel* for multiple subprojects inside a monorepo

        ALL_SOURCE_DIRS = [f"--source-directory={source_dir}" for source_dir in files]
        cmd = (
            ["pyre", "--noninteractive", "--output=json"] + ALL_SOURCE_DIRS + ["check"]
        )
        return self.execute(cmd, capture_output=True).stdout
