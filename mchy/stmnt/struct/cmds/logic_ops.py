
from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar


class SmtNotCmd(SmtCmd):

    def __init__(self, input_atom: SmtAtom, out_var: SmtVar) -> None:
        self.inp: SmtAtom = input_atom
        self.out_var: SmtVar = out_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.out_var)} = not({repr(self.inp)}))"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out_var)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to perform boolean Not targeting output variable without an objective value ({repr(self)})"
            )
        if isinstance(self.inp, SmtVar):
            inp_vdat: SmtVarLinkage = linker.lookup_var(self.inp)
            if not isinstance(inp_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to perform boolean Not using input variable without an objective value ({repr(self)})"
                )
            return [
                ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                ComCmd(
                    f"execute if score {inp_vdat.var_name} {inp_vdat.get_objective(stack_level)} matches 1.. run " +
                    f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"
                ),
            ]
        elif isinstance(self.inp, SmtConstInt):
            return [
                ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} {'0' if self.inp.value <= 0 else '1'}"),
            ]
        else:
            raise VirtualRepError(f"Invalid Not input type `{type(self.inp)}`?")


class SmtAndCmd(SmtCmd):

    def __init__(self, lhs: SmtAtom, rhs: SmtAtom, output_var: SmtVar) -> None:
        self.lhs: SmtAtom = lhs
        self.rhs: SmtAtom = rhs
        self.out: SmtVar = output_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.out)} = ({repr(self.lhs)} and {repr(self.rhs)}))"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to perform boolean and targeting output variable without an objective value ({repr(self)})"
            )
        rhs_vdat: SmtVarLinkage
        if isinstance(self.lhs, SmtVar):
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to perform And using lhs variable without an objective value ({repr(self)})"
                )
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform And using rhs variable without an objective value ({repr(self)})"
                    )
                return [
                    ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"),
                    ComCmd(
                        f"execute if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches 1.. " +
                        f"if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches 1.. run " +
                        f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"
                    ),
                ]
            elif isinstance(self.rhs, SmtConstInt):
                if self.rhs.value >= 1:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"),
                    ]
                else:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"),
                        ComCmd(
                            f"execute if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches 1.. run " +
                            f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"
                        ),
                    ]
            else:
                raise VirtualRepError(f"Invalid And rhs type `{type(self.rhs)}`? (lhs: VAR)")
        elif isinstance(self.lhs, SmtConstInt):
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform And using rhs variable without an objective value ({repr(self)})"
                    )
                if self.lhs.value >= 1:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"),
                    ]
                else:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"),
                        ComCmd(
                            f"execute if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches 1.. run " +
                            f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"
                        ),
                    ]
            elif isinstance(self.rhs, SmtConstInt):
                raise VirtualRepError(f"Constant And comparison encountered at statement representation layer?")
            else:
                raise VirtualRepError(f"Invalid And rhs type `{type(self.rhs)}`? (lhs: INT)")
        else:
            raise VirtualRepError(f"Invalid And lhs type `{type(self.lhs)}`?")


class SmtOrCmd(SmtCmd):

    def __init__(self, lhs: SmtAtom, rhs: SmtAtom, output_var: SmtVar) -> None:
        self.lhs: SmtAtom = lhs
        self.rhs: SmtAtom = rhs
        self.out: SmtVar = output_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.out)} = ({repr(self.lhs)} or {repr(self.rhs)}))"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to perform boolean or targeting output variable without an objective value ({repr(self)})"
            )
        rhs_vdat: SmtVarLinkage
        if isinstance(self.lhs, SmtVar):
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to perform or using lhs variable without an objective value ({repr(self)})"
                )
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform or using rhs variable without an objective value ({repr(self)})"
                    )
                return [
                    ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                    ComCmd(
                        f"execute if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches ..0 " +
                        f"if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches ..0 run " +
                        f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"
                    ),
                ]
            elif isinstance(self.rhs, SmtConstInt):
                if self.rhs.value >= 1:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                    ]
                else:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                        ComCmd(
                            f"execute if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches ..0 run " +
                            f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"
                        ),
                    ]
            else:
                raise VirtualRepError(f"Invalid or rhs type `{type(self.rhs)}`? (lhs: VAR)")
        elif isinstance(self.lhs, SmtConstInt):
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform or using rhs variable without an objective value ({repr(self)})"
                    )
                if self.lhs.value >= 1:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                    ]
                else:
                    return [
                        ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"),
                        ComCmd(
                            f"execute if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches ..0 run " +
                            f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"
                        ),
                    ]
            elif isinstance(self.rhs, SmtConstInt):
                raise VirtualRepError(f"Constant or comparison encountered at statement representation layer?")
            else:
                raise VirtualRepError(f"Invalid or rhs type `{type(self.rhs)}`? (lhs: INT)")
        else:
            raise VirtualRepError(f"Invalid or lhs type `{type(self.lhs)}`?")
