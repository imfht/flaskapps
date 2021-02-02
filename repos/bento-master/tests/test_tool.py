import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Pattern, Type, Union

from bento.base_context import BaseContext
from bento.parser import Parser
from bento.tool import output
from bento.violation import Violation

THIS_PATH = Path(os.path.dirname(__file__))


def result_for(path: Path) -> Violation:
    return Violation(
        tool_id="test",
        check_id="test",
        path=str(path),
        line=0,
        column=0,
        message="test",
        severity=2,
        syntactic_context="test",
    )


def context_for(
    tmp_path: Path,
    tool_id: str,
    base_path: Path = THIS_PATH.parent,
    config: Optional[Dict[str, Any]] = None,
) -> BaseContext:
    return BaseContext(
        base_path=base_path,
        config={"tools": {tool_id: config or {}}},
        cache_path=tmp_path / "cache",
        resource_path=tmp_path / "resource",
    )


class ParserFixture(Parser):
    def parse(self, tool_output: str) -> List[Violation]:
        return [result_for(Path(f)) for f in tool_output.split(",")]


class ToolFixture(output.Str):
    def __init__(
        self,
        tmp_path: Path,
        base_path: Path = THIS_PATH.parent,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context_for(tmp_path, "test", base_path, config))

    @property
    def parser_type(self) -> Type[Parser]:
        return ParserFixture

    @classmethod
    def tool_id(self) -> str:
        return "test"

    @property
    def project_name(self) -> str:
        return "Test"

    @classmethod
    def tool_desc(cls) -> str:
        return "test description"

    @property
    def file_name_filter(self) -> Pattern:
        return re.compile(r"test_tool\.py")

    def matches_project(self, files: Iterable[Path]) -> bool:
        return True

    def setup(self) -> None:
        pass

    def run(self, files: Iterable[str]) -> str:
        return ",".join(files)


def _relpath(path: Union[str, Path]) -> Path:
    return THIS_PATH / path


def test_file_path_filter_terminal(tmp_path: Path) -> None:
    tool = ToolFixture(tmp_path)
    input = [_relpath(p) for p in ["test_tool.py", "foo.py"]]
    result = tool.filter_paths(input)
    expectation = {_relpath("test_tool.py")}

    assert result == expectation


def test_file_path_match(tmp_path: Path) -> None:
    tool = ToolFixture(tmp_path)
    result = tool.filter_paths([_relpath("test_tool.py")])
    expectation = {_relpath("test_tool.py")}

    assert result == expectation


def test_file_path_no_match(tmp_path: Path) -> None:
    tool = ToolFixture(tmp_path)
    search_path = _relpath(Path("integration") / "simple")
    result = tool.filter_paths([search_path])

    assert not result


def test_tool_run_file(tmp_path: Path) -> None:
    tool = ToolFixture(tmp_path)
    result = tool.results([THIS_PATH / "test_tool.py"])

    assert result == [result_for(_relpath("test_tool.py"))]


def test_tool_run_ignores(tmp_path: Path) -> None:
    tool = ToolFixture(tmp_path, config={"ignore": ["test"]})
    result = tool.results([_relpath("test_tool.py")])

    assert not result
