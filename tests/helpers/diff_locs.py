

from typing import List
from mchy.common.com_loc import ComLoc


def loc_diff(observed: ComLoc, expected: ComLoc) -> str:
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
