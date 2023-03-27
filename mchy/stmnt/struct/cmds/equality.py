
from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import InertCoreTypes, InertType
from mchy.errors import StatementRepError, VirtualRepError
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtPseudoVar, SmtVar


class SmtCompEqualityCmd(SmtCmd):

    def __init__(
                self,
                lhs: SmtAtom,
                rhs: SmtAtom,
                output_var: SmtVar,
                clobber_reg1: SmtPseudoVar,
                clobber_reg2: SmtPseudoVar,
                clobber_reg3: SmtPseudoVar,
                clobber_reg4: SmtPseudoVar
            ) -> None:
        self.lhs: SmtAtom = lhs
        self.rhs: SmtAtom = rhs
        self.out: SmtVar = output_var
        # The reg's will be clobbered and must have scoreboard objectives attached (be of type int)
        self.value_reg: SmtPseudoVar = clobber_reg1
        self.null_reg1: SmtPseudoVar = clobber_reg2
        self.null_reg2: SmtPseudoVar = clobber_reg3
        self.null_out_reg: SmtPseudoVar = clobber_reg4
        reg1_type = self.value_reg.get_type()
        reg2_type = self.null_reg1.get_type()
        reg3_type = self.null_reg2.get_type()
        reg4_type = self.null_out_reg.get_type()
        if (not isinstance(reg1_type, InertType)) or (not reg1_type.is_intable()):
            raise StatementRepError(f"Attempted to create Equality Statement with register1 of type `{reg1_type.render()}` `int` required!")
        if (not isinstance(reg2_type, InertType)) or (not reg2_type.is_intable()):
            raise StatementRepError(f"Attempted to create Equality Statement with register2 of type `{reg2_type.render()}` `int` required!")
        if (not isinstance(reg3_type, InertType)) or (not reg3_type.is_intable()):
            raise StatementRepError(f"Attempted to create Equality Statement with register3 of type `{reg3_type.render()}` `int` required!")
        if (not isinstance(reg4_type, InertType)) or (not reg4_type.is_intable()):
            raise StatementRepError(f"Attempted to create Equality Statement with register4 of type `{reg4_type.render()}` `int` required!")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.lhs)} == {repr(self.rhs)})"

    def _values_match_commands(self, linker: 'SmtLinker', stack_level: int, out_reg_vdat: SmtObjVarLinkage) -> List[ComCmd]:
        rhs_vdat: SmtVarLinkage
        if isinstance(self.lhs, SmtVar):
            # get lhs var data
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to test equality using lhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
                )
            if isinstance(self.rhs, SmtVar):
                # get rhs var data
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to test equality using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_reg_vdat.var_name} {out_reg_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} = {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                return [ComCmd(
                    f"execute store result score {out_reg_vdat.var_name} {out_reg_vdat.get_objective(stack_level)} run execute " +
                    f"if score {lhs_vdat.var_name} {lhs_vdat.get_objective(stack_level)} matches {self.rhs.value}"
                )]
            else:
                raise VirtualRepError(f"Invalid equality rhs type `{type(self.lhs)}`? (lhs: var)")
        elif isinstance(self.lhs, SmtConstInt):
            if isinstance(self.rhs, SmtVar):
                # get rhs var data
                rhs_vdat = linker.lookup_var(self.rhs)
                if not isinstance(rhs_vdat, SmtObjVarLinkage):
                    raise VirtualRepError(
                        f"Attempted to test equality using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
                    )
                return [ComCmd(
                    f"execute store result score {out_reg_vdat.var_name} {out_reg_vdat.get_objective(stack_level)} run execute " +
                    f"if score {rhs_vdat.var_name} {rhs_vdat.get_objective(stack_level)} matches {self.lhs.value}"
                )]
            elif isinstance(self.rhs, SmtConstInt):
                raise VirtualRepError(f"Constant Equality comparison encountered at statement representation layer?")
            else:
                raise VirtualRepError(f"Invalid equality rhs type `{type(self.lhs)}`? (lhs: int)")
        else:
            raise VirtualRepError(f"Invalid equality lhs type `{type(self.lhs)}`?")

    def _null_match_commands(self, linker: 'SmtLinker', stack_level: int, out_reg_vdat: SmtObjVarLinkage) -> List[ComCmd]:
        # get registers
        null_reg1_vdat = linker.lookup_var(self.null_reg1)
        if not isinstance(null_reg1_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to test equality using clobber register variable without an objective value ({repr(self.null_reg1)} --- {null_reg1_vdat})"
            )
        null_reg2_vdat = linker.lookup_var(self.null_reg2)
        if not isinstance(null_reg2_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to test equality using clobber register variable without an objective value ({repr(self.null_reg2)} --- {null_reg2_vdat})"
            )

        # Get expr types
        lhs_type = self.lhs.get_type()
        rhs_type = self.rhs.get_type()
        if not isinstance(lhs_type, InertType):
            raise VirtualRepError(f"lhs_type is not Inert in equality")
        if not isinstance(rhs_type, InertType):
            raise VirtualRepError(f"rhs_type is not Inert in equality")

        # resolve never null case
        if (lhs_type.nullable is False and lhs_type.target != InertCoreTypes.NULL) and (rhs_type.nullable is False and rhs_type.target != InertCoreTypes.NULL):
            return [ComCmd(f"scoreboard players set {out_reg_vdat.var_name} {out_reg_vdat.get_objective(stack_level)} 1")]

        cmds: List[ComCmd] = []

        # Get lhs null-ness into the scoreboard
        if lhs_type.target != InertCoreTypes.NULL:
            cmds.append(ComCmd(f"scoreboard players set {null_reg1_vdat.var_name} {null_reg1_vdat.get_objective(stack_level)} 1"))
        elif lhs_type.nullable:
            # Int constants aren't nullable so this should be a variable
            # Get var data:
            if not isinstance(self.lhs, SmtVar):
                raise VirtualRepError(f"Non-var encountered for a nullable lhs? ({repr(self.lhs)})")
            lhs_vdat: SmtVarLinkage = linker.lookup_var(self.lhs)
            if not isinstance(lhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to test equality using lhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
                )
            # Build cmd
            cmds.append(ComCmd(
                f"execute store result score {null_reg1_vdat.var_name} {null_reg1_vdat.get_objective(stack_level)} run " +
                f"data get storage {lhs_vdat.get_store_path(stack_level)}.{lhs_vdat.var_name}.is_null"
            ))
        else:
            cmds.append(ComCmd(f"scoreboard players set {null_reg1_vdat.var_name} {null_reg1_vdat.get_objective(stack_level)} 0"))

        # Get rhs null-ness into the scoreboard
        if rhs_type.target != InertCoreTypes.NULL:
            cmds.append(ComCmd(f"scoreboard players set {null_reg2_vdat.var_name} {null_reg2_vdat.get_objective(stack_level)} 1"))
        elif rhs_type.nullable:
            # Int constants aren't nullable so this should be a variable
            # Get var data:
            if not isinstance(self.rhs, SmtVar):
                raise VirtualRepError(f"Non-var encountered for a nullable rhs? ({repr(self.rhs)})")
            rhs_vdat: SmtVarLinkage = linker.lookup_var(self.rhs)
            if not isinstance(rhs_vdat, SmtObjVarLinkage):
                raise VirtualRepError(
                    f"Attempted to test equality using rhs variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
                )
            # Build cmd
            cmds.append(ComCmd(
                f"execute store result score {null_reg2_vdat.var_name} {null_reg2_vdat.get_objective(stack_level)} run " +
                f"data get storage {rhs_vdat.get_store_path(stack_level)}.{rhs_vdat.var_name}.is_null"
            ))
        else:
            cmds.append(ComCmd(f"scoreboard players set {null_reg2_vdat.var_name} {null_reg2_vdat.get_objective(stack_level)} 0"))

        # make the output register hold if the 2 calculation registers are equal
        cmds.append(ComCmd(
            f"execute store result score {out_reg_vdat.var_name} {out_reg_vdat.get_objective(stack_level)} run execute " +
            f"if score {null_reg1_vdat.var_name} {null_reg1_vdat.get_objective(stack_level)} = {null_reg2_vdat.var_name} {null_reg2_vdat.get_objective(stack_level)}"
        ))

        return cmds

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        # Get registers
        out_vdat: SmtVarLinkage = linker.lookup_var(self.out)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to test equality targeting output variable without an objective value ({repr(self.out)} = {self.lhs.get_type()} == {self.rhs.get_type()})"
            )
        out_vreg_vdat = linker.lookup_var(self.value_reg)
        if not isinstance(out_vreg_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to test equality using clobber register variable without an objective value ({repr(self.value_reg)} --- {out_vreg_vdat})"
            )
        out_nreg_vdat = linker.lookup_var(self.null_out_reg)
        if not isinstance(out_nreg_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to test equality using clobber register variable without an objective value ({repr(self.null_out_reg)} --- {out_nreg_vdat})"
            )

        cmds: List[ComCmd] = []

        # Only compare values if neither side is a null literal
        lhs_type = self.lhs.get_type()
        rhs_type = self.rhs.get_type()
        if (isinstance(lhs_type, InertType) and lhs_type.target == InertCoreTypes.NULL) or (isinstance(rhs_type, InertType) and rhs_type.target == InertCoreTypes.NULL):
            cmds.append(ComCmd(f"scoreboard players set {out_vreg_vdat.var_name} {out_vreg_vdat.get_objective(stack_level)} 1"))
        else:
            cmds.extend(self._values_match_commands(linker, stack_level, out_vreg_vdat))

        # compare nullness
        cmds.extend(self._null_match_commands(linker, stack_level, out_nreg_vdat))

        # 'And' results to output
        cmds.append(ComCmd(f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 0"))
        cmds.append(ComCmd(
            f"execute if score {out_vreg_vdat.var_name} {out_vreg_vdat.get_objective(stack_level)} matches 1 " +
            f"if score {out_nreg_vdat.var_name} {out_nreg_vdat.get_objective(stack_level)} matches 1 run " +
            f"scoreboard players set {out_vdat.var_name} {out_vdat.get_objective(stack_level)} 1"
        ))
        return cmds
