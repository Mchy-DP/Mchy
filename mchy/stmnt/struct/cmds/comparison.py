
from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar


class SmtCompGTECmd(SmtCmd):

    def __init__(self, lhs: SmtAtom, rhs: SmtAtom, output_var: SmtVar) -> None:
        self.lhs: SmtAtom = lhs
        self.rhs: SmtAtom = rhs
        self.out: SmtVar = output_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.lhs)} >= {repr(self.rhs)})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to perform GTE targeting output variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} >= {self.rhs.get_type()})"
            )
        rhs_vdat: SmtVarLinkage
        if isinstance(self.lhs, SmtVar):
            # get lhs var data
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to perform GTE using lhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} >= {self.rhs.get_type()})"
                )
            # find rhs type
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform GTE using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} >= {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} >= {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches {self.rhs.value}.."
                )]
            else:
                raise VirtualRepError(f"Invalid GTE rhs type `{type(self.rhs)}`? (LHS: var)")
        elif isinstance(self.lhs, SmtConstInt):
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform GTE using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} >= {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches ..{self.lhs.value}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                raise VirtualRepError(f"Constant GTE comparison encountered at statement representation layer?")
            else:
                raise VirtualRepError(f"Invalid GTE rhs type `{type(self.rhs)}`? (LHS: int)")
        else:
            raise VirtualRepError(f"Invalid GTE lhs type `{type(self.lhs)}`?")


class SmtCompGTCmd(SmtCmd):

    def __init__(self, lhs: SmtAtom, rhs: SmtAtom, output_var: SmtVar) -> None:
        self.lhs: SmtAtom = lhs
        self.rhs: SmtAtom = rhs
        self.out: SmtVar = output_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.lhs)} > {repr(self.rhs)})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to perform GT targeting output variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} > {self.rhs.get_type()})"
            )
        rhs_vdat: SmtVarLinkage
        if isinstance(self.lhs, SmtVar):
            # get lhs var data
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to perform GT using lhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} > {self.rhs.get_type()})"
                )
            # find rhs type
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform GT using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} > {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} > {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches {self.rhs.value+1}.."
                )]
            else:
                raise VirtualRepError(f"Invalid GT rhs type `{type(self.rhs)}`? (LHS: var)")
        elif isinstance(self.lhs, SmtConstInt):
            if isinstance(self.rhs, SmtVar):
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to perform GT using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} > {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run execute " +
                    f"if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches ..{self.lhs.value-1}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                raise VirtualRepError(f"Constant GT comparison encountered at statement representation layer?")
            else:
                raise VirtualRepError(f"Invalid GT rhs type `{type(self.rhs)}`? (LHS: int)")
        else:
            raise VirtualRepError(f"Invalid GT lhs type `{type(self.lhs)}`?")
