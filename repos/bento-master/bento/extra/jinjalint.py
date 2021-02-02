import json
import re
from pathlib import Path
from typing import Iterable, List, Optional, Pattern, Type

from semantic_version import SimpleSpec

from bento.parser import Parser
from bento.tool import output, runner
from bento.violation import Violation


"""
Input example:

[
  {
    "message": "flask apps using 'flask-wtf' require including a csrf token in the html form. this check detects missing csrf protection in html forms in jinja templates.",
    "physical_line": "        <form method=\"post\">",
    "code": "jinjalint-form-missing-csrf-protection",
    "file_path": "jinja-template.html",
    "line": 7,
    "column": 8
  },
  {
    "message": "pages opened with 'target=\"_blank\"' allow the new page to access the original's 'window.opener'. this can have security and performance implications. include 'rel=\"noopener\"' to prevent this.",
    "physical_line": "        <a href=\"https://example.com\" target=\"_blank\">test anchor</a>",
    "code": "jinjalint-anchor-missing-noopener",
    "file_path": "jinja-template.html",
    "line": 11,
    "column": 8
  },
  {
    "message": "pages opened with 'target=\"_blank\"' allow the new page to access the original's referrer. this can have privacy implications. include 'rel=\"noreferrer\"' to prevent this.",
    "physical_line": "        <a href=\"https://example.com\" target=\"_blank\">test anchor</a>",
    "code": "jinjalint-anchor-missing-noreferrer",
    "file_path": "jinja-template.html",
    "line": 11,
    "column": 8
  }
]
"""


class JinjalintParser(Parser[str]):
    CHECK_PREFIX = "jinjalint-"
    CHECK_PREFIX_LEN = len(CHECK_PREFIX)
    SEVERITY = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

    @staticmethod
    def _get_link(code: str) -> Optional[str]:
        if "recursion-error" in code or "parse-error" in code:
            # These errors do not have documentation
            return None

        code_suffix = code.replace(JinjalintParser.CHECK_PREFIX, "")
        return f"https://bento.dev/checks/jinja/{code_suffix}/"

    def parse(self, tool_output: str) -> List[Violation]:
        results = json.loads(tool_output)

        violations = [
            Violation(
                check_id=r["code"].replace(self.CHECK_PREFIX, ""),
                tool_id=JinjalintTool.TOOL_ID,
                path=self.trim_base(r["file_path"]),
                severity=JinjalintParser.SEVERITY["MEDIUM"],
                line=r["line"],
                column=r["column"],
                message=r["message"],
                syntactic_context=r.get("physical_line", ""),
                link=self._get_link(r["code"]),
            )
            for r in results
        ]

        return violations


class JinjalintTool(runner.Python, output.Str):
    TOOL_ID = "r2c.jinja"
    VENV_DIR = "jinjalint"
    PROJECT_NAME = "Python"
    JINJA_FILE_NAME_FILTER = re.compile(
        r".*\.(html|jinja|jinja2|j2|twig)$"
    )  # Jinjalint's default extensions
    PACKAGES = {"r2c-jinjalint": SimpleSpec("~=0.7.1")}

    @property
    def shebang_pattern(self) -> Optional[Pattern]:
        return None

    @property
    def parser_type(self) -> Type[Parser]:
        return JinjalintParser

    @classmethod
    def tool_id(self) -> str:
        return JinjalintTool.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Finds common security issues in Jinja templates"

    @classmethod
    def venv_subdir_name(cls) -> str:
        return JinjalintTool.VENV_DIR

    @property
    def project_name(self) -> str:
        return JinjalintTool.PROJECT_NAME

    @property
    def file_name_filter(self) -> Pattern:
        return JinjalintTool.JINJA_FILE_NAME_FILTER

    def matches_project(self, files: Iterable[Path]) -> bool:
        has_jinja = any((self.JINJA_FILE_NAME_FILTER.match(p.name) for p in files))
        has_python = any((self.PYTHON_FILE_PATTERN.match(p.name) for p in files))
        return has_jinja and has_python

    def run(self, paths: Iterable[str]) -> str:
        launchpoint: str = str(self.venv_dir() / "bin" / "jinjalint")
        exclude_rules = [
            "--exclude",
            "jinjalint-space-only-indent",
            "--exclude",
            "jinjalint-misaligned-indentation",
        ]
        cmd = ["python", launchpoint, "--json"] + exclude_rules + list(paths)
        return self.venv_exec(cmd, check_output=False)
