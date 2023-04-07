from typing import List
from mchy.common.com_types import ExecCoreTypes, ExecType
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.function import SmtFunc
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtExecVarLinkage
from mchy.stmnt.struct.cmds import SmtCleanupTag
from mchy.errors import VirtualRepError


def get_cleanup_stmnts(smt_func: SmtFunc, linker: 'SmtLinker', stack_level: int) -> List[SmtCmd]:
    """Yield a list of statements that must be executed at the end of the function regardless of how the function exits (similar to closing a file or freeing memory)

    Returns:
        The list of commands to fully cleanup this function
    """
    cmds: List[SmtCmd] = []
    for var in smt_func.get_all_vars():
        var_dat: SmtVarLinkage = linker.lookup_var(var)
        if isinstance(var_dat, SmtExecVarLinkage):
            var_type = var.get_type()
            if not isinstance(var_type, ExecType):
                raise VirtualRepError("Variable with executable linkage is not of executable type?")
            if var_type.target == ExecCoreTypes.WORLD:
                continue  # World tags can never be assigned to so don't need to be cleanup up
            cmds.append(SmtCleanupTag(var_dat.get_full_tag(stack_level)))
    return cmds
