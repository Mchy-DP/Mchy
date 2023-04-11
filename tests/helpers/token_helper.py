from dataclasses import dataclass
from itertools import zip_longest
from typing import Optional, Tuple
from mchy.mchy_ast.mchy_parser import MchyCustomParser

from tests.helpers.util import EscapeColors


@dataclass(eq=True)
class TokRep:
    type_int: int
    token_text: Optional[str] = None

    @property
    def type_str(self) -> str:
        return MchyCustomParser.symbolicNames[self.type_int]

    def __str__(self) -> str:
        return f"{self.type_str}" + (f"(`{repr(self.token_text)[1:-1]}`)" if self.token_text is not None else "")


def compare_tok_reps(obs_tok_reps, exp_tok_reps, color=False) -> Tuple[bool, str]:
    max_width_lhs = 0  # rhs width unimportant as no text justification needed
    comparison_output: list[Tuple[str, str, str]] = []
    compared_equal = True
    for observed_tok, expected_tok in zip_longest(obs_tok_reps, exp_tok_reps, fillvalue=None):
        prelude = "UNKNOWN"
        lhs = str(observed_tok)
        rhs = str(expected_tok)
        if observed_tok is None:
            prelude = "MISSING"
            lhs = ""
        elif expected_tok is None:
            prelude = "EXTRA"
            rhs = ""
        else:
            if expected_tok.token_text is None:
                if expected_tok.type_int == observed_tok.type_int:
                    prelude = "MATCH"
                else:
                    prelude = "MISMATCH"
            else:
                if expected_tok == observed_tok:
                    prelude = "MATCH"
                else:
                    prelude = "MISMATCH"

        if prelude != "MATCH":
            compared_equal = False

        # width fixing:
        if len(lhs) > 45:
            lhs = lhs[:42] + "..."
        if len(rhs) > 45:
            rhs = rhs[:42] + "..."
        max_width_lhs = max(max_width_lhs, len(lhs))

        comparison_output.append((prelude, lhs, rhs))

    # Build summary string
    summary_string = ""
    comparison_output.insert(0, ("", "Observed", "Expected"))
    for prelude, lhs, rhs in comparison_output:
        line = ""
        if color is True:
            if prelude == "MATCH":
                line += EscapeColors.ENDC + EscapeColors.GREEN
            elif prelude == "":
                line += EscapeColors.ENDC + EscapeColors.YELLOW
            else:
                line += EscapeColors.ENDC + EscapeColors.DARK_RED
        line += f"{prelude}: ".lstrip(":").ljust(10) + lhs.rjust(max_width_lhs) + " | " + rhs
        if color is True:
            line += EscapeColors.ENDC
        summary_string += line + "\n"

    return compared_equal, "Token mismatch:\n" + summary_string
