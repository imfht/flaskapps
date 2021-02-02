import json
from typing import Any, Dict, Iterable, List, Mapping, Type

from semantic_version import SimpleSpec

from bento.parser import Parser
from bento.tool import output, runner
from bento.violation import Violation

# Input example:
# {
#     "./foo.py": [
#         {
#             "code": "E124",
#             "filename": "./foo.py",
#             "line_number": 2,
#             "column_number": 9,
#             "text": "closing bracket does not match visual indentation",
#             "physical_line": "        )\n"
#         }
#     ]
# }
#

# Only these prefixes will be inspected
RULE_PREFIXES = "B,C90,E113,E74,E9,EXE,F,T100,W6"

FLAKE8_TO_BENTO = {
    "B001": "bare-except-bugbear",
    "B002": "unsupported-unary-increment",
    "B003": "assignment-to-environ",
    "B004": "unreliable-hasattr-call",
    "B005": "no-multicharacter-strip",
    "B006": "no-mutable-default-args",
    "B007": "unused-loop-variable",
    "B008": "no-call-in-default-args",
    "B009": "no-getattr",
    "B010": "no-setattr",
    "B011": "no-assert-false",
    "B012": "escaped-finally",
    "B301": "no-iter-methods",
    "B302": "no-view-methods",
    "B303": "no-metaclass",
    "B304": "no-maxint",
    "B305": "no-next-method",
    "B306": "no-exception-message-method",
    "C90": "too-complex",
    "E113": "indentation-error",
    "E701": "multiple-statements-colon",
    "E702": "multiple-statements-semicolon",
    "E703": "ending-semicolon",
    "E704": "multiple-statements-def",
    "E711": "none-comparison",
    "E712": "true-comparison",
    "E713": "membership-test",
    "E714": "identity-test",
    "E721": "type-comparison",
    "E722": "bare-except",
    "E731": "no-assign-lambda",
    "E741": "ambiguous-variable-name",
    "E742": "ambiguous-class-name",
    "E743": "ambiguous-function-name",
    "E901": "syntax-error",
    "E902": "io-error",
    "E999": "parse-error",
    "EXE001": "not-executable",
    "EXE002": "missing-shebang",
    "EXE003": "not-python",
    "EXE004": "whitespace-before-shebang",
    "EXE005": "lines-before-shebang",
    "F401": "unused-module",
    "F402": "shadowed-import",
    "F403": "wildcard-import",
    "F404": "future-import-order",
    "F405": "undefined-module-name",
    "F406": "bad-wildcard-import",
    "F601": "dict-key-repeated",
    "F602": "dict-key-variable-repeated",
    "F621": "too-many-expressions-with-star",
    "F622": "more-than-one-star-in-assignment",
    "F631": "assert-tuple-always-true",
    "F632": "use-eqeq-for-literals",
    "F633": "invalid-arrows-with-print",
    "F811": "redefined-unused-name",
    "F812": "redefined-name",
    "F821": "undefined-name",
    "F822": "undefined-name-in-all",
    "F823": "unassigned-variable",
    "F831": "duplicated-argument",
    "F841": "unused-variable",
    "T100": "debugger",
    "W601": "deprecated-has-key",
    "W602": "deprecated-raise",
    "W603": "deprecated-inequality",
    "W604": "deprecated-backticks",
    "W605": "invalid-escape",
    "W606": "bad-async-or-await",
}


class Flake8Parser(Parser[str]):
    @classmethod
    def to_bento(cls) -> Mapping[str, str]:
        return FLAKE8_TO_BENTO

    @staticmethod
    def id_to_link(check_id: str) -> str:
        if check_id == "E999":
            link = ""
        elif check_id.startswith("B"):
            link = "https://github.com/PyCQA/flake8-bugbear/blob/master/README.rst#list-of-warnings"
        elif check_id == "T100":
            link = "https://github.com/JBKahn/flake8-debugger/blob/master/README.md"
        elif check_id.startswith("EXE"):
            link = "https://github.com/xuhdev/flake8-executable/blob/master/README.md#flake8-executable"
        elif check_id.startswith("F6"):
            link = "https://flake8.pycqa.org/en/latest/user/error-codes.html"
        elif check_id in ("E722", "E306", "E117", "E113", "W606"):
            link = "https://pycodestyle.readthedocs.io/en/latest/intro.html#error-codes"
        else:
            link = f"https://lintlyci.github.io/Flake8Rules/rules/{check_id}.html"
        return link

    @classmethod
    def id_to_name(cls, check_id: str) -> str:
        return cls.to_bento().get(check_id, check_id)

    @staticmethod
    def tool() -> Type[output.Str]:
        return Flake8Tool

    def to_violation(self, result: Dict[str, Any]) -> Violation:
        source = (result["physical_line"] or "").rstrip()  # Remove trailing whitespace
        path = self.trim_base(result["filename"])

        check_id = result["code"]

        return Violation(
            tool_id=self.tool().tool_id(),
            check_id=self.id_to_name(check_id),
            path=path,
            line=result["line_number"],
            column=result["column_number"],
            message=result["text"],
            severity=2,
            syntactic_context=source,
            link=self.id_to_link(check_id),
        )

    def parse(self, tool_output: str) -> List[Violation]:
        results: Dict[str, List[Dict[str, Any]]] = json.loads(tool_output)
        return [self.to_violation(v) for r in results.values() for v in r]


class Flake8Tool(runner.Python, output.Str):
    TOOL_ID = "flake8"  # to-do: versioning?
    VENV_DIR = "flake8"
    PROJECT_NAME = "Python"
    PACKAGES = {
        "flake8": SimpleSpec("~=3.7.0"),
        "flake8-json": SimpleSpec("~=19.8.0"),
        "flake8-bugbear": SimpleSpec("~=20.1.4"),
        "flake8-debugger": SimpleSpec("~=3.2.0"),
    }

    @property
    def parser_type(self) -> Type[Parser]:
        return Flake8Parser

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    @classmethod
    def tool_desc(cls) -> str:
        return "Finds common bugs in Python code"

    @property
    def project_name(self) -> str:
        return self.PROJECT_NAME

    @classmethod
    def venv_subdir_name(self) -> str:
        return self.VENV_DIR

    def select_clause(self) -> str:
        """Returns a --select argument to identify which checks flake8 should run"""
        return f"--select={RULE_PREFIXES}"

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
