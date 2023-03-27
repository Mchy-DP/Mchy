
from typing import List


def helper_extract_lines_between(text: str, start: str, end: str, complete_match: bool = True) -> List[str]:
    start = start.strip("\n\r\t ")
    end = end.strip("\n\r\t ")

    relevant_lines: List[str] = []
    tracking: bool = False
    for line in text.split("\n"):
        line = line.strip("\n\r\t ")
        if (complete_match and line == end) or ((not complete_match) and (end in line)):
            tracking = False
        if tracking:
            relevant_lines.append(line)
        if (complete_match and line == start) or ((not complete_match) and (start in line)):
            tracking = True

    return relevant_lines
