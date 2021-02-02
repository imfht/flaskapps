import json
from typing import Iterable, List, Type

from semantic_version import SimpleSpec

from bento.parser import Parser
from bento.tool import output, runner
from bento.violation import Violation

"""
Input example:

{
    "/path/to/file.py": [
        {
            "code": "DUO105",
            "filename": "/path/to/file.py",
            "line_number": 24,
            "column_number": 1,
            "text": "use of \"exec\" is insecure",
            "physical_line": "exec('foo')\n"
        }
    ]
}
"""

DLINT_TO_BENTO = {"DUO138": "regular-expression-catastrophic-backtracking"}


class DlintParser(Parser[str]):
    SEVERITY = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

    @staticmethod
    def _get_link(code: str) -> str:
        return "https://github.com/dlint-py/dlint/blob/master/docs/linters/{}.md".format(
            code
        )

    def parse(self, tool_output: str) -> List[Violation]:
        results = json.loads(tool_output)

        violations = [
            Violation(
                check_id=DLINT_TO_BENTO[result["code"]],
                tool_id=DlintTool.TOOL_ID,
                path=self.trim_base(filename),
                severity=DlintParser.SEVERITY["MEDIUM"],
                line=result["line_number"],
                column=result["column_number"],
                message=result["text"],
                syntactic_context=(result["physical_line"] or "").rstrip(),
                link=self._get_link(result["code"]),
            )
            for filename, file_results in results.items()
            for result in file_results
        ]

        return violations


class DlintTool(runner.Python, output.Str):
    TOOL_ID = "dlint"
    VENV_DIR = "dlint"
    PROJECT_NAME = "Python"
    PACKAGES = {"dlint": SimpleSpec("~=0.10.2"), "flake8-json": SimpleSpec("~=19.8.0")}

    @property
    def parser_type(self) -> Type[Parser]:
        return DlintParser

    @classmethod
    def tool_id(self) -> str:
        return DlintTool.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "A tool for encouraging best coding practices and helping ensure Python code is secure"

    @classmethod
    def venv_subdir_name(cls) -> str:
        return DlintTool.VENV_DIR

    @property
    def project_name(self) -> str:
        return DlintTool.PROJECT_NAME

    def select_clause(self) -> str:
        return f"--select={','.join(DLINT_TO_BENTO.keys())}"

    def run(self, paths: Iterable[str]) -> str:
        cmd = [
            "python",
            str(self.venv_dir() / "bin" / "flake8"),
            self.select_clause(),
            "--format=json",
            "--isolated",
            *paths,
        ]
        return self.venv_exec(cmd, check_output=False)
