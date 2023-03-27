
from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar


class SmtPlusCmd(SmtCmd):
    """Only used for math addition (different statement for exec merging)"""

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} + {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to perform mathematical-plus on a variable without an objective value ({self.target_var.get_type()} + {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to add a variable without an objective value ({self.target_var.get_type()} + {self.value.get_type()})")
            return [ComCmd(
                f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} += {source_vdat.var_name} {source_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(f"scoreboard players add {target_vdat.var_name} {target_vdat.get_objective(stack_level)} {self.value.value}")]
        else:
            raise VirtualRepError(f"Invalid addition value type `{type(self.value)}`?")


class SmtMinusCmd(SmtCmd):

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} - {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to perform mathematical-minus on a variable without an objective value ({self.target_var.get_type()} - {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to minus a variable without an objective value ({self.target_var.get_type()} - {self.value.get_type()})")
            return [ComCmd(
                f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} -= {source_vdat.var_name} {source_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(f"scoreboard players remove {target_vdat.var_name} {target_vdat.get_objective(stack_level)} {self.value.value}")]
        else:
            raise VirtualRepError(f"Invalid minus value type `{type(self.value)}`?")


class SmtMultCmd(SmtCmd):

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} * {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to multiply a variable without an objective value ({self.target_var.get_type()} * {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to multiply by a variable without an objective value ({self.target_var.get_type()} * {self.value.get_type()})")
            return [ComCmd(
                f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} *= {source_vdat.var_name} {source_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            linker.add_const(self.value.value)
            return [ComCmd(f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} *= c{self.value.value} {linker.get_const_obj()}")]
        else:
            raise VirtualRepError(f"Invalid multiply value type `{type(self.value)}`?")


class SmtDivCmd(SmtCmd):

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} / {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to perform integer division on variable without an objective value ({self.target_var.get_type()} // {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to perform integer division by a variable without an objective value ({self.target_var.get_type()} // {self.value.get_type()})")
            return [ComCmd(
                f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} /= {source_vdat.var_name} {source_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            linker.add_const(self.value.value)
            return [ComCmd(f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} /= c{self.value.value} {linker.get_const_obj()}")]
        else:
            raise VirtualRepError(f"Invalid integer division denominator type `{type(self.value)}`?")


class SmtModCmd(SmtCmd):

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.target_var)} % {self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if not isinstance(target_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to perform modulo division on variable without an objective value ({self.target_var.get_type()} % {self.value.get_type()})")
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if not isinstance(source_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to perform modulo division by a variable without an objective value ({self.target_var.get_type()} % {self.value.get_type()})")
            return [ComCmd(
                f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} %= {source_vdat.var_name} {source_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            linker.add_const(self.value.value)
            return [ComCmd(f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(stack_level)} %= c{self.value.value} {linker.get_const_obj()}")]
        else:
            raise VirtualRepError(f"Invalid modulo division denominator type `{type(self.value)}`?")
