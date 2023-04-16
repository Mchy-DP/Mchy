
from typing import List, Tuple
from mchy.stmnt.struct import *
from mchy.stmnt.struct.cmds.tag_ops import SmtRawEntitySelector
from tests.helpers.util import EscapeColors


def _clamp(n: int, smallest: int, largest: int) -> int:
    """Return n if it is in the range `smallest` to `largest` (inclusive) else return the the limit

    Args:
        n: The value to constrain
        smallest: The minimum value n will be returned as
        largest: The maximum value n will be returned as

    Returns:
        int: n or the limit if n was outside the range
    """
    return max(smallest, min(n, largest))


def _atom_eq(atom1: SmtAtom, atom2: SmtAtom) -> bool:
    """
    Returns True if the 2 supplied atoms have equal data (even if they are not the same atom by id)
    """
    if type(atom1) != type(atom2):
        return False
    if isinstance(atom1, SmtPublicVar) and isinstance(atom2, SmtPublicVar):
        return atom1.name == atom2.name
    elif isinstance(atom1, SmtPseudoVar) and isinstance(atom2, SmtPseudoVar):
        return atom1.value == atom2.value
    elif isinstance(atom1, SmtConstNull) and isinstance(atom2, SmtConstNull):
        return True
    elif isinstance(atom1, SmtConstInt) and isinstance(atom2, SmtConstInt):
        return atom1.value == atom2.value
    elif isinstance(atom1, SmtConstFloat) and isinstance(atom2, SmtConstFloat):
        return atom1.value == atom2.value
    elif isinstance(atom1, SmtConstStr) and isinstance(atom2, SmtConstStr):
        return atom1.value == atom2.value
    elif isinstance(atom1, SmtWorld) and isinstance(atom2, SmtWorld):
        return True
    else:
        raise TypeError(f"Unsupported atom type {type(atom1)}")


def _cmd_eq(cmd1: SmtCmd, cmd2: SmtCmd) -> bool:
    """
    Returns True if the 2 supplied commands have equal data (even if they are not the same command by id)
    """
    if type(cmd1) != type(cmd2):
        return False
    if isinstance(cmd1, SmtAssignCmd) and isinstance(cmd2, SmtAssignCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtInvokeFuncCmd) and isinstance(cmd2, SmtInvokeFuncCmd):
        return cmd1.func_id == cmd2.func_id
    elif isinstance(cmd1, SmtConditionalInvokeFuncCmd) and isinstance(cmd2, SmtConditionalInvokeFuncCmd):
        return (
            cmd1.func_id == cmd2.func_id and
            cmd1.ext_frag.get_frag_name() == cmd2.ext_frag.get_frag_name() and
            len(cmd1.conditions) == len(cmd2.conditions) and
            all(((cmd1_cond[1] == cmd2_cond[1]) and _atom_eq(cmd1_cond[0], cmd2_cond[0])) for cmd1_cond, cmd2_cond in zip(cmd1.conditions, cmd2.conditions))
        )
    elif isinstance(cmd1, SmtPlusCmd) and isinstance(cmd2, SmtPlusCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtMinusCmd) and isinstance(cmd2, SmtMinusCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtMultCmd) and isinstance(cmd2, SmtMultCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtDivCmd) and isinstance(cmd2, SmtDivCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtModCmd) and isinstance(cmd2, SmtModCmd):
        return _atom_eq(cmd1.target_var, cmd2.target_var) and _atom_eq(cmd1.value, cmd2.value)
    elif isinstance(cmd1, SmtCompEqualityCmd) and isinstance(cmd2, SmtCompEqualityCmd):
        return _atom_eq(cmd1.lhs, cmd2.lhs) and _atom_eq(cmd1.rhs, cmd2.rhs) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtCompGTECmd) and isinstance(cmd2, SmtCompGTECmd):
        return _atom_eq(cmd1.lhs, cmd2.lhs) and _atom_eq(cmd1.rhs, cmd2.rhs) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtCompGTCmd) and isinstance(cmd2, SmtCompGTCmd):
        return _atom_eq(cmd1.lhs, cmd2.lhs) and _atom_eq(cmd1.rhs, cmd2.rhs) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtNotCmd) and isinstance(cmd2, SmtNotCmd):
        return _atom_eq(cmd1.inp, cmd2.inp) and _atom_eq(cmd1.out_var, cmd2.out_var)
    elif isinstance(cmd1, SmtAndCmd) and isinstance(cmd2, SmtAndCmd):
        return _atom_eq(cmd1.lhs, cmd2.lhs) and _atom_eq(cmd1.rhs, cmd2.rhs) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtOrCmd) and isinstance(cmd2, SmtOrCmd):
        return _atom_eq(cmd1.lhs, cmd2.lhs) and _atom_eq(cmd1.rhs, cmd2.rhs) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtNullCoalCmd) and isinstance(cmd2, SmtNullCoalCmd):
        return _atom_eq(cmd1.opt_atom, cmd2.opt_atom) and _atom_eq(cmd1.def_atom, cmd2.def_atom) and _atom_eq(cmd1.out, cmd2.out)
    elif isinstance(cmd1, SmtRawEntitySelector) and isinstance(cmd2, SmtRawEntitySelector):
        return _atom_eq(cmd1.executor, cmd2.executor) and _atom_eq(cmd1.target_var, cmd2.target_var) and cmd1.selector == cmd2.selector
    else:
        raise TypeError(f"Unsupported cmd type {type(cmd1).__name__}")


def diff_cmds_list(observed_cmds: List[SmtCmd], expected_cmds: List[SmtCmd], color: bool = True, cull_comments: bool = True) -> Tuple[bool, str]:
    """Yeild the diffrences between the observed commands and the expected ones

    Args:
        observed_cmds: The commands observed during test
        expected_cmds: The commands that were exepected to be generated
        color: If terminal-color should be included in the debug output. Defaults to True.
        cull_comments: If observed datapack-comments should be ignored. Defaults to True.

    Returns:
        Tuple[bool, str]:
          * return[0] -> True if the commands match.
          * return[1] -> A human readable debug string indicating the mismatches.
    """
    if cull_comments:
        observed_cmds = list(filter(lambda x: not isinstance(x, SmtCommentCmd), observed_cmds))
    explanation: List[Tuple[str, str, str]] = []
    match: bool = True
    mismatch_limit = 5
    while len(expected_cmds) > 0:
        c_expected, *expected_cmds = expected_cmds
        if len(observed_cmds) == 0:
            explanation.append(("MISSING", "", str(c_expected)))
            match = False
            continue
        c_observed, *observed_cmds = observed_cmds
        if _cmd_eq(c_expected, c_observed):
            explanation.append(("MATCH", str(c_observed), str(c_expected)))
        else:
            match = False
            if any(_cmd_eq(ocmd, c_expected) for ocmd in observed_cmds):
                while not _cmd_eq(c_observed, c_expected):
                    explanation.append(("EXTRA", str(c_observed), ""))
                    c_observed, *observed_cmds = observed_cmds
                explanation.append(("MATCH", str(c_observed), str(c_expected)))
            else:
                # There is never a match for this expected command
                if any(_cmd_eq(ecmd, c_observed) for ecmd in expected_cmds):
                    while not _cmd_eq(c_observed, c_expected):
                        explanation.append(("MISSING", "", str(c_expected)))
                        c_expected, *expected_cmds = expected_cmds
                    explanation.append(("MATCH", str(c_observed), str(c_expected)))
                else:
                    # complete mismatch
                    explanation.append(("MISMATCH", str(c_observed), str(c_expected)))
                    mismatch_limit -= 1
                    if mismatch_limit <= 0:
                        explanation.append(("STOP", "Too mismatched to continue", "Too mismatched to continue"))
                        break
    # leftover observed commands
    for c_observed in observed_cmds:
        explanation.append(("EXTRA", str(c_observed), ""))
        match = False

    # render found diff to string:
    expl_str = ""
    ocol_size = _clamp(max((len(ocol) for _, ocol, _ in explanation), default=0), 10, 75)
    for match_type, obs, exp in explanation:
        lnstr = f"{match_type.rjust(8)}: {obs.rjust(ocol_size)} | {exp}"
        if color:
            if match_type == "MATCH":
                lnstr = EscapeColors.GREEN + lnstr + EscapeColors.ENDC
            elif match_type == "MISMATCH":
                lnstr = EscapeColors.RED + lnstr + EscapeColors.ENDC
            else:
                lnstr = EscapeColors.YELLOW + lnstr + EscapeColors.ENDC
        expl_str += lnstr + "\n"
    return match, expl_str
