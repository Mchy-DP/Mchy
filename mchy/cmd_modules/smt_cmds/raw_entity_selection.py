

from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtVar, SmtWorld
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtRawEntitySelector(SmtCmd):

    def __init__(self, executor: SmtAtom, target_var: SmtVar, selector: str) -> None:
        self.executor: SmtAtom = executor
        self.target_var: SmtVar = target_var
        self.selector: str = selector

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} = {self.selector})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if isinstance(self.executor, SmtWorld):
            executor_selection = ""
        elif isinstance(self.executor, SmtVar):
            exec_vdat = linker.lookup_var(self.executor)
            if not isinstance(exec_vdat, SmtExecVarLinkage):
                raise VirtualRepError(f"Attempted to execute as variable `{exec_vdat.var_name}` without attached tag")
            executor_selection = f"execute as {exec_vdat.get_selector(stack_level)} at @s run "
        else:
            raise VirtualRepError(f"Executor is neither world nor var, {self.executor} encountered")
        target_vdat = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Attempted to assign selector to variable `{target_vdat.var_name}` without attached tag.  (selector: {self.selector})")
        return [ComCmd(f"{executor_selection}tag {self.selector} add {target_vdat.get_full_tag(stack_level)}")]
