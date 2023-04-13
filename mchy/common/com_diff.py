

from typing import List, Optional
import difflib


DID_YOU_MEAN = "Did you mean:"


def how_similar(str1: str, str2: str) -> float:
    str1_lower = str1.lower()
    str2_lower = str2.lower()
    return difflib.SequenceMatcher(None, str1_lower, str2_lower).ratio()


def is_similar(str1: str, str2: str) -> bool:
    # Return True if the similarity score is above a threshold
    return how_similar(str1, str2) >= 0.8


def did_you_mean_opt(bad_str: str, valid_options: List[str]) -> List[str]:
    opts = difflib.get_close_matches(bad_str, valid_options)
    if len(opts) >= 2:
        if how_similar(bad_str, opts[0]) >= (how_similar(bad_str, opts[1]) + 0.25):
            # if theres a clear winner (first is 25% better than the best second place) then return just the best match
            return [opts[0]]
    return opts


def did_you_mean_str(bad_str: str, valid_options: List[str]) -> Optional[str]:
    """Give a string of the form `Did you mean: <OPTS>?` where OPTS are nicely formatted or None if no options could be found"""
    did_u_mean = did_you_mean_opt(bad_str, valid_options)
    if len(did_u_mean) == 0:
        return None
    # add `'s to all suggestions
    did_u_mean = [f"`{suggestion}`" for suggestion in did_u_mean]
    if len(did_u_mean) == 1:
        return f"{DID_YOU_MEAN} {did_u_mean[-1]}?"
    return f"{DID_YOU_MEAN} {' or '.join([', '.join(did_u_mean[:-1]), did_u_mean[-1]])}?"
