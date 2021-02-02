import json
from collections import OrderedDict
from typing import Any, Dict, List, Mapping, Set, TextIO, Union

import attr

from bento.violation import Violation

VIOLATIONS_KEY = "violations"

Hash = str
ToolId = str
Baseline = Dict[str, Set[Hash]]
ToolResults = Mapping[str, Mapping[Hash, Mapping[str, Any]]]


def filtered(
    tool_id: str, output: List[Violation], baseline: Baseline
) -> List[Violation]:
    rejects: Set[Hash] = set(baseline.get(tool_id, {}))
    return [
        attr.evolve(v, filtered=v.syntactic_identifier_str() in rejects) for v in output
    ]


def dump_results(results: List[Violation]) -> Dict[str, Dict[Hash, Dict[str, Any]]]:
    with_hashes: Dict[str, Dict[str, Any]] = OrderedDict(
        sorted(
            ((v.syntactic_identifier_str(), v.to_dict()) for v in results),
            key=(lambda vv: vv[0]),
        )
    )
    return {VIOLATIONS_KEY: with_hashes}


def write_tool_results(stream: TextIO, results: Mapping[ToolId, ToolResults]) -> None:
    json.dump(results, stream, indent=2)


def load_baseline(text: Union[str, TextIO]) -> Mapping[str, ToolResults]:
    parsed = json.loads(text) if isinstance(text, str) else json.load(text)
    return parsed or {}


def json_to_violation_hashes(text: Union[str, TextIO]) -> Baseline:
    parsed = load_baseline(text)
    out = {}
    for (tool_id, r) in parsed.items():
        violations = r[VIOLATIONS_KEY]
        hashes = set(violations.keys()) if violations else set()
        out[tool_id] = hashes
    return out


def to_cache_repr(findings: List[Violation]) -> str:
    as_dict = [attr.asdict(f) for f in findings]
    return json.dumps(as_dict)


def from_cache_repr(text: str) -> List[Violation]:
    parsed = json.loads(text)
    return [Violation(**kwargs) for kwargs in parsed]
