import os
from pathlib import Path

from bento.extra.pyre import PyreTool
from tests.test_tool import context_for

THIS_PATH = Path(os.path.dirname(__file__))
BASE_PATH = THIS_PATH / ".." / ".." / ".."

# Pyre is turned off, as it does not work with explicit paths

# def test_run(tmp_path: Path) -> None:
#     base_path = BASE_PATH / "tests/integration/py-only"
#     tool = PyreTool(context_for(tmp_path, PyreTool.TOOL_ID, base_path))
#     tool.setup()
#     violations = tool.results()
#
#     expectation = [
#         Violation(
#             tool_id="pyre",
#             check_id="6",
#             path="bar.py",
#             line=10,
#             column=13,
#             message="Incompatible parameter type [6]: Expected `int` for 1st anonymous parameter to call `int.__radd__` but got `str`.",
#             severity=2,
#             syntactic_context="    x: int = cmd + 5 + os.getenv('doesnotexist')\n",
#             link="https://pyre-check.org/docs/error-types.html",
#         ),
#         Violation(
#             tool_id="pyre",
#             check_id="6",
#             path="bar.py",
#             line=10,
#             column=23,
#             message="Incompatible parameter type [6]: Expected `int` for 1st anonymous parameter to call `int.__add__` but got `typing.Optional[str]`.",
#             severity=2,
#             syntactic_context="    x: int = cmd + 5 + os.getenv('doesnotexist')\n",
#             link="https://pyre-check.org/docs/error-types.html",
#         ),
#         Violation(
#             tool_id="pyre",
#             check_id="7",
#             path="bar.py",
#             line=11,
#             column=4,
#             message="Incompatible return type [7]: Expected `str` but got `None`.",
#             severity=2,
#             syntactic_context="    return None\n",
#             link="https://pyre-check.org/docs/error-types.html",
#         ),
#     ]
#
#     assert set(violations) == set(expectation)


def test_file_match(tmp_path: Path) -> None:
    f = PyreTool(context_for(tmp_path, PyreTool.TOOL_ID)).file_name_filter

    assert f.match("py") is None
    assert f.match("foo.py") is not None
    assert f.match("foo.pyi") is None
