import json
import re
from typing import Any, Dict, Iterable, List, Optional, Pattern, Type

from bento.parser import Parser
from bento.tool import JsonR, output, runner
from bento.util import fetch_line_in_file
from bento.violation import Violation


class ShellcheckParser(Parser[JsonR]):
    def to_violation(self, result: Dict[str, Any]) -> Violation:

        path = self.trim_base(result["file"])
        start_line = result["line"]
        start_col = result["column"]
        message = result.get("message", "")
        check_id = f"SC{result['code']}"

        level = result["level"]
        severity = 0
        if level == "error":
            severity = 2
        elif level == "warning":
            severity = 1

        link = f"https://github.com/koalaman/shellcheck/wiki/{check_id}"
        line_of_code = (
            fetch_line_in_file(self.base_path / path, start_line) or "<no source found>"
        )

        return Violation(
            tool_id=ShellcheckTool.tool_id(),
            check_id=check_id,
            path=path,
            line=start_line,
            column=start_col,
            message=message,
            severity=severity,
            syntactic_context=line_of_code,
            link=link,
        )

    def parse(self, results: JsonR) -> List[Violation]:
        violations: List[Violation] = []
        for check in results:
            violations.append(self.to_violation(check))
        return violations


class ShellcheckTool(runner.Docker, output.Json):
    DOCKER_IMAGE = "koalaman/shellcheck:v0.7.0"
    FILE_NAME_FILTER = re.compile(r".*\.(sh|bash|ksh|dash)$")
    CONTAINER_NAME = "bento-shell-check-daemon"
    TOOL_ID = "shellcheck"
    SHEBANG_PATTERN = re.compile(r"^#!(.*/|.*env +)(sh|bash|ksh)")

    @property
    def shebang_pattern(self) -> Optional[Pattern]:
        return self.SHEBANG_PATTERN

    @property
    def parser_type(self) -> Type[Parser]:
        return ShellcheckParser

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Finds bugs in shell scripts (requires Docker)"

    @property
    def file_name_filter(self) -> Pattern:
        return self.FILE_NAME_FILTER

    @property
    def project_name(self) -> str:
        return "Shell"

    @property
    def docker_image(self) -> str:
        return self.DOCKER_IMAGE

    @property
    def remote_code_path(self) -> str:
        return "/mnt/"

    @property
    def docker_command(self) -> List[str]:
        return ["--severity", "info", "-f", "json"]

    def is_allowed_returncode(self, returncode: int) -> bool:
        return returncode == 0 or returncode == 1

    def run(self, files: Iterable[str]) -> JsonR:
        result = self.run_container(files)
        return json.loads(result.stdout)
