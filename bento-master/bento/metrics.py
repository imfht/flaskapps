import itertools
import os
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Optional, Tuple

import bento.git
from bento.constants import ARGS_TO_EXCLUDE_FROM_METRICS
from bento.util import read_global_config
from bento.violation import Violation

USAGE_SALT = "566F73BE939D2383A93F9D5759328".encode()
RESULTS_SALT = "266DD8584C42A12FC9447B1F9AFC6".encode()


def __hash_sha256(data: Optional[str], salt: bytes) -> Optional[str]:
    """ Get SHA256 of data
    """
    if data is None:
        return None

    hsh = sha256(salt)
    hsh.update(data.encode())
    return hsh.hexdigest()


def __get_filtered_violation_count(violations: Iterable[Violation]) -> int:
    return sum(1 for v in violations if v.filtered)


def __get_aggregate_violations(violations: List[Violation]) -> List[Dict[str, Any]]:
    """Returns count of violation per file, per check_id"""

    def grouping(v: Violation) -> Tuple[str, str]:
        return v.path, v.check_id

    out = []
    for k, v in itertools.groupby(sorted(violations, key=grouping), grouping):
        p, rid = k
        out.append(
            {
                "path_hash": __hash_sha256(p, RESULTS_SALT),
                "check_id": rid,
                "count": sum(1 for _ in v),
                "filtered_count": __get_filtered_violation_count(v),
            }
        )
    return out


def _infer_ci_provider() -> str:
    """Returns used CI provider based on environment."""
    if os.getenv("BENTO_ACTION") == "true":
        return "github-actions/bento-action"

    # https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables
    elif os.getenv("GITHUB_ACTIONS") == "true":
        return "github-actions"

    # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
    elif os.getenv("CIRCLECI") == "true":
        return "circleci"

    # https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
    elif os.getenv("TRAVIS") == "true":
        return "travis"

    # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    elif os.getenv("GITLAB_CI") == "true":
        return "gitlab-ci"

    elif os.getenv("CI"):
        return "unknown"

    else:
        return "none"


def violations_to_metrics(
    tool_id: str, timestamp: str, violations: List[Violation], ignores: List[str]
) -> List[Dict[str, Any]]:
    # NOTE: Do not calculate url() and commit() on a per-item basis.
    # Doing so causes bento check to take many unnecessary seconds.
    url = bento.git.url()
    commit = bento.git.commit()
    return [
        {
            "tool": tool_id,
            "timestamp": timestamp,
            "hash_of_repository": __hash_sha256(url, RESULTS_SALT),
            "hash_of_commit": __hash_sha256(commit, RESULTS_SALT),
            "ignored_rules": ignores,
            **aggregates,
        }
        for aggregates in __get_aggregate_violations(violations)
    ]


def read_user_email() -> Optional[str]:
    # email guaranteed to exist because we check it for every command
    global_config = read_global_config()
    if not global_config:
        return None

    return global_config.get("email")


def command_metric(
    command: str,
    email: str,
    timestamp: str,
    command_kwargs: Dict[str, Any],
    exit_code: int,
    duration: float,
    exception_name: Optional[str],
    user_duration: Optional[float] = None,
) -> List[Dict[str, Any]]:

    # remove kwargs that contain sensitive data from metrics
    kwargs_to_exclude = ARGS_TO_EXCLUDE_FROM_METRICS.get(command, set())
    command_kwargs = dict(
        (k, v) for k, v in command_kwargs.items() if k not in kwargs_to_exclude
    )

    d = {
        "timestamp": timestamp,
        "duration": duration,
        "user_duration": user_duration,
        "exit_code": exit_code,
        "hash_of_repository": __hash_sha256(bento.git.url(), USAGE_SALT),
        "email": email,
        "hash_of_commit": __hash_sha256(bento.git.commit(), USAGE_SALT),
        "command": command,
        "command_kwargs": command_kwargs,
        "is_ci": bool(os.environ.get("CI", False)),
        "ci_provider": _infer_ci_provider(),
        "exception_name": exception_name,
    }
    return [d]
