

from enum import Enum, auto


class EscapeColors:
    DARK_RED = "\033[31m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    ENDC = "\033[0m"


class _Diff_lvl(Enum):
    MATCH = auto()     # Identical
    PARTIAL = auto()   # No immediate mismatches but not comparing equal
    PROPERTY = auto()  # A property does not match (includes wrong children count)
    UNKNOWN = auto()   # Mismatched but in a unknown way
    MISMATCH = auto()  # A complete mismatch
