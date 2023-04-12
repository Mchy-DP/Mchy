

from typing import List
from mchy.common.com_loc import ComLoc


def loc_diff(observed: ComLoc, expected: ComLoc) -> str:
    if (
                any((x is not None) for x in [expected.line, expected.line_end, expected.col_start, expected.col_end]) and
                all((x is None) for x in [observed.line, observed.line_end, observed.col_start, observed.col_end])
            ):
        return f"Observed location UNSET while expecting at least some data: (Expected: {repr(expected)})"
    out: List[str] = []
    if observed.line != expected.line:
        out.append(f"line: {observed.line} != {expected.line}")
    if observed.col_start != expected.col_start:
        out.append(f"col_start: {observed.col_start} != {expected.col_start}")
    if observed.col_end != expected.col_end:
        out.append(f"col_end: {observed.col_end} != {expected.col_end}")
    if observed.line_end != expected.line_end:
        out.append(f"line_end: {observed.line_end} != {expected.line_end}")
    return ", ".join(out)
