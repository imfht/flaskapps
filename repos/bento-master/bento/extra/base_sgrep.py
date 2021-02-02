import json
import re
from abc import abstractmethod
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Pattern

from bento.parser import Parser
from bento.tool import JsonR, output, runner
from bento.util import fetch_line_in_file
from bento.violation import Violation


class BaseSgrepParser(Parser[JsonR]):
    @classmethod
    @abstractmethod
    def tool_id(cls) -> str:
        pass

    def parse(self, results: JsonR) -> List[Violation]:
        violations: List[Violation] = []
        for check in results:
            check_id = check["check_id"]
            path = self.trim_base(check["path"])
            start_line = check["start"]["line"]
            start_col = check["start"]["col"]
            # Custom way to get check_name for sgrep-lint:0.1.10
            message = check.get("extra", {}).get("message")
            source = (
                fetch_line_in_file(self.base_path / path, start_line)
                or "<no source found>"
            ).rstrip()
            violation = Violation(
                tool_id=self.tool_id(),
                check_id=check_id,
                path=path,
                line=start_line,
                column=start_col,
                message=message,
                severity=2,
                syntactic_context=source,
            )

            violations.append(violation)
        return violations


class BaseSgrepTool(runner.Docker, output.Json):
    DOCKER_IMAGE = "returntocorp/sgrep:0.4.8"
    FILE_NAME_FILTER = re.compile(r".*")

    @property
    @abstractmethod
    def config_str(self) -> str:
        """
        Returns the configuration argument to pass to sgrep
        """
        pass

    def get_config_path(self) -> Optional[Path]:
        """
        Returns the path to the sgrep configuration file _if it is a path_.
        Returns None otherwise.
        """
        return None

    @property
    def docker_image(self) -> str:
        return self.DOCKER_IMAGE

    @property
    def remote_code_path(self) -> str:
        return "/home/repo"

    @property
    def additional_file_targets(self) -> Mapping[Path, str]:
        config_path = self.get_config_path()
        if config_path:
            return {config_path: self.config_str}
        else:
            return {}

    @property
    def docker_command(self) -> List[str]:
        return ["--config", self.config_str, "--json", "--skip-pattern-validation"]

    @property
    def file_name_filter(self) -> Pattern:
        return self.FILE_NAME_FILTER

    @property
    def project_name(self) -> str:
        return "Python/JS"

    @classmethod
    def tool_desc(cls) -> str:
        return "Runs checks from r2c's check registry (experimental; requires Docker)"

    def run(self, files: Iterable[str]) -> JsonR:
        output_str = self.run_container(files).stdout.split("\n")
        stdout = output_str[-2]  # last line is blank
        output = json.loads(stdout)
        return output.get("results", [])
