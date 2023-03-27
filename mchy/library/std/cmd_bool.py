from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.errors import ConversionError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstInt, SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtLinker, SmtObjVarLinkage, SmtVarLinkage


class SmtCastBoolCmd(SmtCmd):

    def __init__(self, inp: SmtAtom, output_var: SmtVar) -> None:
        self.inp: SmtAtom = inp
        self.out_var: SmtVar = output_var

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.out_var)} = bool({repr(self.inp)}))"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        output_vdat: SmtVarLinkage = linker.lookup_var(self.out_var)
        if not isinstance(output_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Attempted to perform bool-cast targeting a variable without an objective value ({repr(self)})")
        if isinstance(self.inp, SmtConstInt):
            return [
                ComCmd(f"scoreboard players set {output_vdat.var_name} {output_vdat.get_objective(stack_level)} {'0' if self.inp.value <= 0 else '1'}"),
            ]
        elif isinstance(self.inp, SmtVar):
            inp_vdat: SmtVarLinkage = linker.lookup_var(self.inp)
            if not isinstance(inp_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Attempted to perform bool-cast using a variable without an objective value ({repr(self)})")
            return [
                ComCmd(f"scoreboard players set {output_vdat.var_name} {output_vdat.get_objective(stack_level)} 0"),
                ComCmd(
                    f"execute if score {inp_vdat.var_name} {inp_vdat.get_objective(stack_level)} matches 1.. run " +
                    f"scoreboard players set {output_vdat.var_name} {output_vdat.get_objective(stack_level)} 1"
                ),
            ]
        else:
            raise VirtualRepError(f"Bool input is not Int or Var, found: `{type(self.inp).__name__}`")


class CmdSay(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "bool"

    def get_params(self) -> Sequence[IParam]:
        return [IParam("x", InertType(InertCoreTypes.INT))]

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.BOOL)

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.BOOL))
        return [
            SmtCastBoolCmd(param_binding["x"], output_register)
        ], output_register
