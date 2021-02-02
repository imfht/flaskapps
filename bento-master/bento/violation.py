import binascii
import textwrap
from typing import Any, Dict, Optional

import attr
import pymmh3 as mmh3


@attr.s(frozen=True, hash=False)
class Violation:
    """
    N.B.: line and column are 1-based, not 0-based
    """

    BASELINE_IGNORED_ITEMS = ["line", "column", "link", "filtered"]

    tool_id = attr.ib(type=str)
    check_id = attr.ib(type=str)
    path = attr.ib(type=str)
    # cmp is deprecated, but we need to use it for compatibility with 18.x.
    line = attr.ib(type=int, hash=None, cmp=False)
    column = attr.ib(type=int, hash=None, cmp=False)
    message = attr.ib(type=str, hash=None, cmp=False)
    severity = attr.ib(type=int, hash=None, cmp=False)
    syntactic_context = attr.ib(type=str, converter=textwrap.dedent)
    semantic_context = None
    filtered = attr.ib(type=Optional[bool], default=None, hash=None, cmp=False)
    link = attr.ib(type=Optional[str], default=None, hash=None, cmp=False, kw_only=True)

    def syntactic_identifier_int(self) -> int:
        # Use murmur3 hash to minimize collisions

        str_id = str((self.check_id, self.path, self.syntactic_context))
        return mmh3.hash128(str_id)

    def syntactic_identifier_str(self) -> str:
        id_bytes = int.to_bytes(
            self.syntactic_identifier_int(), byteorder="big", length=16, signed=False
        )
        return str(binascii.hexlify(id_bytes), "ascii")

    def __hash__(self) -> int:
        # attr.s equality uses all elements of syntactic_identifier, so
        # hash->equality contract is guaranteed
        return self.syntactic_identifier_int()

    def to_dict(self) -> Dict[str, Any]:
        d = attr.asdict(self)
        for i in Violation.BASELINE_IGNORED_ITEMS:
            d.pop(i)
        return d
