

from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar, SmtWorld


class SmtTagMergeCmd(SmtCmd):
    """Only used for math addition (different statement for exec merging)"""

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} + {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Attempted to perform tag-merge on a variable without a tag ({self.target_var.get_type()} + {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtExecVarLinkage):
                raise VirtualRepError(f"Attempted to tag-merge a variable without a tag ({self.target_var.get_type()} + {self.value.get_type()})")
            return [ComCmd(f"tag {source_vdat.get_selector(stack_level)} add {target_vdat.get_full_tag(stack_level)}")]
        else:
            raise VirtualRepError(f"Invalid tag-merge value type `{type(self.value)}`?")


class SmtTagRemoveCmd(SmtCmd):
    """Only used for math subtraction (different statement for exec merging)"""

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} + {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Attempted to perform tag-remove on a variable without a tag ({self.target_var.get_type()} - {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtExecVarLinkage):
                raise VirtualRepError(f"Attempted to tag-remove a variable without a tag ({self.target_var.get_type()} - {self.value.get_type()})")
            return [ComCmd(f"tag {source_vdat.get_selector(stack_level)} remove {target_vdat.get_full_tag(stack_level)}")]
        else:
            raise VirtualRepError(f"Invalid tag-remove value type `{type(self.value)}`?")


class SmtRawEntitySelector(SmtCmd):
    """Assign the target_var to the entities selected by a raw selector"""

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
        return [
            ComCmd(f"tag {target_vdat.get_selector(stack_level, force_group=True)} remove {target_vdat.get_full_tag(stack_level)}"),
            ComCmd(f"{executor_selection}tag {self.selector} add {target_vdat.get_full_tag(stack_level)}")
        ]
