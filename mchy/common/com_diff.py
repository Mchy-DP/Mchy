

from typing import List
import difflib


def how_similar(str1: str, str2: str) -> float:
    str1_lower = str1.lower()
    str2_lower = str2.lower()
    return difflib.SequenceMatcher(None, str1_lower, str2_lower).ratio()


def is_similar(str1: str, str2: str) -> bool:
    # Return True if the similarity score is above a threshold
    return how_similar(str1, str2) >= 0.8


def did_you_mean_opt(bad_str: str, valid_options: List[str]) -> List[str]:
    return difflib.get_close_matches(bad_str, valid_options)
