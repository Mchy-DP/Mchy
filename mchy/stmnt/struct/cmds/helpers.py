
from typing import List, Tuple, Union
from mchy.common.com_cmd import ComCmd
from mchy.errors import StatementRepError
from mchy.stmnt.helpers import smt_get_exec_vdat
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar, SmtWorld
from mchy.stmnt.struct.function import SmtFunc, SmtMchyFunc
from mchy.stmnt.struct.smt_frag import SmtFragment


def resolve_condition_cmd(conditions: List[Tuple[Union[SmtConstInt, SmtVar], bool]], linker: SmtLinker, stack_level: int) -> str:
    """Given a list of conditions that must at runtime hold a given value generate the exeucte command bod that will only pass if the conditions are met

    e.g.:
    [(1, True), (foo, False)] ---> if score var_foo objective matches ..0

    """
    cmd: str = ""
    for cond, req_value in conditions:
        if isinstance(cond, SmtConstInt):
            # If it's constant resolve the condition at compile time
            if ((req_value is True) and (cond.value <= 0)) or ((req_value is False) and (cond.value >= 1)):
                return "if entity @p[tag=foo,tag=!foo]"  # Cannot resolve true
        elif isinstance(cond, SmtVar):
            cond_vdat: SmtVarLinkage = linker.lookup_var(cond)
            if not isinstance(cond_vdat, SmtObjVarLinkage):
                raise StatementRepError("Variable without scoreboard reached late-stage conditional fragment resolution")
            if req_value:
                cmd += f" if score {cond_vdat.var_name} {cond_vdat.get_objective(stack_level)} matches 1.."
            else:
                cmd += f" if score {cond_vdat.var_name} {cond_vdat.get_objective(stack_level)} matches ..0"
        else:
            raise StatementRepError(f"condition had invalid type {type(cond)}, expected SmtConstInt or SmtVar")
    return cmd.strip(" ")
