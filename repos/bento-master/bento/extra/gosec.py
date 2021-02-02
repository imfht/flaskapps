import json
import re
import sys
from pathlib import PurePath
from typing import Any, Dict, Iterable, List, Pattern, Type

from bento.parser import Parser
from bento.tool import JsonR, output, runner
from bento.util import fetch_line_in_file
from bento.violation import Violation

REMOTE_BASE_PATH = PurePath("/mnt")


class GosecParser(Parser[JsonR]):
    SEVERITIES = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}

    def to_violation(self, result: Dict[str, Any]) -> Violation:
        start_line = int(result["line"])
        column = int(result["column"])
        check_id = result["rule_id"]
        message = result["details"]
        path = str(PurePath(result["file"]).relative_to(REMOTE_BASE_PATH))

        level = result["severity"]
        severity = self.SEVERITIES.get(level, 0)

        link = result.get("cwe", {}).get("URL", "")

        line_of_code = (
            fetch_line_in_file(self.base_path / path, start_line) or "<no source found>"
        )

        return Violation(
            tool_id=GosecTool.TOOL_ID,
            check_id=check_id,
            path=path,
            line=start_line,
            column=column,
            message=message,
            severity=severity,
            syntactic_context=line_of_code,
            link=link,
        )

    def parse(self, results: JsonR) -> List[Violation]:
        return [self.to_violation(r) for r in results]


class GosecTool(runner.Docker, output.Json):
    """
    Runs securego/gosec.

    Note that the runtime of this tool is independent of the number of paths Bento is running on,
    and is always linear in the size of the project, due to limitations of the wrapped gosec interface.
    """

    TOOL_ID = "gosec"
    DOCKER_IMAGE = "securego/gosec:v2.2.0"
    FILE_FILTER = re.compile(r".*\.go$")

    @property
    def parser_type(self) -> Type[Parser]:
        return GosecParser

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Finds security bugs in Go code"

    @property
    def file_name_filter(self) -> Pattern:
        return self.FILE_FILTER

    @property
    def project_name(self) -> str:
        return "Go"

    @property
    def docker_image(self) -> str:
        return self.DOCKER_IMAGE

    @property
    def docker_command(self) -> List[str]:
        return ["--fmt", "json"]

    @property
    def remote_code_path(self) -> str:
        return str(REMOTE_BASE_PATH)

    def is_allowed_returncode(self, returncode: int) -> bool:
        return returncode == 0 or returncode == 1

    # gosec only operates on modules, not individual files, so we
    # set the max batch size to effectively unbounded, and filter the results
    # returned by gosec
    #
    # Unfortunately this means the runtime of gosec is constant with the number
    # of queried paths, and linear in the project size :(
    @classmethod
    def max_batch_size(cls) -> int:
        return sys.maxsize

    def assemble_full_command(self, targets: Iterable[str]) -> List[str]:
        return self.docker_command + [self.remote_code_path]

    def filter_result_paths(self, results: JsonR, files: Iterable[str]) -> JsonR:
        """Filters gosec results to only files that we care about"""
        to_keep = {PurePath(f).relative_to(self.base_path) for f in files}
        return [
            r
            for r in results
            if PurePath(r["file"]).relative_to(REMOTE_BASE_PATH) in to_keep
        ]

    def run(self, files: Iterable[str]) -> JsonR:
        output = self.run_container(files).stdout
        all_results = json.loads(output).get("Issues", [])
        return self.filter_result_paths(all_results, files)
