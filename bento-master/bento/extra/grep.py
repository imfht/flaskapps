import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Pattern, Type

import yaml

from bento.constants import GREP_CONFIG_FILE_NAME
from bento.parser import Parser
from bento.tool import JsonR, output
from bento.violation import Violation


class GrepParser(Parser[JsonR]):
    def to_violation(self, output_rule: Dict[str, Any]) -> Violation:
        output = output_rule["output"]
        check_id = output_rule["id"]
        message = output_rule.get("message")
        parts = output.split(":")
        path = parts[0]
        path = self.trim_base(path)
        line_no = int(parts[1])
        code_snippet = ":".join(parts[2:])
        return Violation(
            tool_id=GrepTool.TOOL_ID,
            check_id=check_id,
            path=path,
            line=line_no,
            column=1,
            message=message or code_snippet,
            severity=2,
            syntactic_context=code_snippet or "<no context>",
        )

    def parse(self, input_json: JsonR) -> List[Violation]:
        return [self.to_violation(r) for r in input_json]


class GrepTool(output.Json):
    TOOL_ID = "grep"  # to-do: versioning?
    PROJECT_NAME = "Grep"

    @property
    def parser_type(self) -> Type[Parser]:
        return GrepParser

    @classmethod
    def tool_id(self) -> str:
        return GrepTool.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Matches user-provided regex patterns (experimental)"

    @property
    def project_name(self) -> str:
        return GrepTool.PROJECT_NAME

    @property
    def file_name_filter(self) -> Pattern:
        return re.compile(r".*\b")

    def extra_cache_paths(self) -> List[Path]:
        return [(self.context.base_path / GREP_CONFIG_FILE_NAME).resolve()]

    def matches_project(self, files: Iterable[Path]) -> bool:
        # disabled by default for now
        return False

    def setup(self) -> None:
        pass  # TODO don't assume grep exists

    def query_rule(
        self, rule: Dict[str, Any], all_source_dirs: List[str]
    ) -> Iterator[str]:
        includes = []

        regex = rule.get("regex")
        if regex:
            file_ext_filters = rule.get("file_extentions", [])
            for file_ext_filter in file_ext_filters:
                includes.extend(["--include", file_ext_filter])
            cmd = ["grep"] + includes + ["-nRI", regex] + all_source_dirs
        yield self.execute(cmd, capture_output=True).stdout

    def run(self, files: Iterable[str]) -> JsonR:
        all_source_dirs = [f"{source_dir}" for source_dir in files]

        try:
            with (self.context.base_path / GREP_CONFIG_FILE_NAME).open() as grep_file:
                yml = yaml.safe_load(grep_file)
            grep_rules = yml.get("patterns", [])
        except FileNotFoundError:
            grep_rules = []

        all_output = [
            {"output": line, **rule}
            for rule in grep_rules
            for output in self.query_rule(rule, all_source_dirs)
            for line in output.split("\n")
            if line
        ]
        return all_output
