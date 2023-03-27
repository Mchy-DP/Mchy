

from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import InertType
from mchy.errors import StatementRepError, VirtualRepError
from mchy.stmnt.struct.cmds.assign import SmtAssignCmd
from mchy.stmnt.struct.cmds.equality import SmtCompEqualityCmd
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtConstNull, SmtPseudoVar, SmtVar


class SmtNullCoalCmd(SmtCmd):

    def __init__(
            self,
            opt_atom: SmtAtom,
            default: SmtAtom,
            output_var: SmtVar,
            clobber_reg1: SmtPseudoVar,
            clobber_reg2: SmtPseudoVar,
            clobber_reg3: SmtPseudoVar,
            clobber_reg4: SmtPseudoVar,
            clobber_reg5: SmtPseudoVar,
            null_const_atom: SmtConstNull
            ) -> None:
        # Store my atoms, vars and registers
        self.opt_atom: SmtAtom = opt_atom
        self.def_atom: SmtAtom = default
        self.out: SmtVar = output_var
        self.opt_null: SmtPseudoVar = clobber_reg1
        # Validate my registers are of valid type
        reg1_type = self.opt_null.get_type()
        if (not isinstance(reg1_type, InertType)) or (not reg1_type.is_intable()):
            raise StatementRepError(f"Attempted to create Null Coalescing Statement with register1 of type `{reg1_type.render()}` `int` required!")
        # Construct sub-statements
        try:
            self.stmt_assign_opt = SmtAssignCmd(self.out, self.opt_atom)
        except StatementRepError as e:
            raise StatementRepError(f"Error instantiating sub-statement 'stmt_assign_opt' of `{type(self).__name__}`") from e
        try:
            self.stmt_assign_def = SmtAssignCmd(self.out, self.def_atom)
        except StatementRepError as e:
            raise StatementRepError(f"Error instantiating sub-statement 'stmt_assign_def' of `{type(self).__name__}`") from e
        try:
            self.stmt_opt_null = SmtCompEqualityCmd(self.opt_atom, null_const_atom, self.opt_null, clobber_reg2, clobber_reg3, clobber_reg4, clobber_reg5)
        except StatementRepError as e:
            raise StatementRepError(f"Error instantiating sub-statement 'stmt_opt_null' of `{type(self).__name__}`") from e

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.out)} = ({repr(self.opt_atom)} or {repr(self.def_atom)}))"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        cmds: List[ComCmd] = []
        # set opt_null to 1 if opt_expr is null
        try:
            opt_null = self.stmt_opt_null.virtualize(linker, stack_level)
        except VirtualRepError as e:
            raise VirtualRepError(f"Error virtualizing sub-statement 'stmt_opt_null' of `{type(self).__name__}`") from e
        cmds.extend(opt_null)

        # build cmd prefixes
        opt_null_vdat = linker.lookup_var(self.opt_null)
        if not isinstance(opt_null_vdat, SmtObjVarLinkage):
            raise VirtualRepError(
                f"Attempted to null coalesce using clobber register (1) variable without an objective value ({repr(self.opt_null)} --- {opt_null_vdat})"
            )
        opt_chosen_prefix = f"execute if score {opt_null_vdat.var_name} {opt_null_vdat.get_objective(stack_level)} matches ..0 run "
        def_chosen_prefix = f"execute if score {opt_null_vdat.var_name} {opt_null_vdat.get_objective(stack_level)} matches 1.. run "

        # append prefixed commands
        try:
            assign_opt = self.stmt_assign_opt.virtualize(linker, stack_level)
        except VirtualRepError as e:
            raise VirtualRepError(f"Error virtualizing sub-statement 'stmt_assign_opt' of `{type(self).__name__}`") from e
        try:
            assign_def = self.stmt_assign_def.virtualize(linker, stack_level)
        except VirtualRepError as e:
            raise VirtualRepError(f"Error virtualizing sub-statement 'stmt_assign_def' of `{type(self).__name__}`") from e

        cmds.extend([ComCmd(opt_chosen_prefix + com_cmd.cmd) for com_cmd in assign_opt])
        cmds.extend([ComCmd(def_chosen_prefix + com_cmd.cmd) for com_cmd in assign_def])
        return cmds
