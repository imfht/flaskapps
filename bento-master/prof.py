import cProfile
import pstats
import sys
from pstats import SortKey  # type: ignore  # noqa


def run(sorting: str, mod: str) -> None:
    if sorting == "time":
        sk = SortKey.TIME
    else:
        sk = SortKey.CUMULATIVE
    cProfile.run(f"import {mod}", "prof.out")
    pstats.Stats("prof.out").sort_stats(sk).print_stats(40)


run(sys.argv[1], sys.argv[2])
