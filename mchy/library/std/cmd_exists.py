from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtObjVarLinkage


class SmtBlockExistsCmd(SmtCmd):

    def __init__(self, location: SmtAtom, required_block: str, out_reg: SmtVar) -> None:
        self.location: SmtAtom = location
        self.required_block: str = required_block
        self.out_reg: SmtVar = out_reg

    def __repr__(self) -> str:
        return f"{type(self).__name__}(loc={self.location}, req_block={self.required_block} ,out_reg={self.out_reg})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, executor = StructPos.build_position_string(get_struct_instance(self.location))
        out_vdat = linker.lookup_var(self.out_reg)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Output register does not have linked scoreboard?")
        if executor is not None:
            exec_vdat = get_exec_vdat(executor, linker)
            return [ComCmd(
                f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} " +
                f"at {exec_vdat.get_selector(stack_level)} run execute if block {pos_str} {self.required_block}"
            )]
        else:
            return [ComCmd(
                f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} " +
                f"run execute if block {pos_str} {self.required_block}"
            )]


class SmtEntityExistsCmd(SmtCmd):

    def __init__(self, entity: SmtAtom, out_reg: SmtVar) -> None:
        self.entity: SmtAtom = entity
        entity_type = self.entity.get_type()
        if not isinstance(entity_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with entity of type {entity_type}, ExecType required")
        self.out_reg: SmtVar = out_reg

    def __repr__(self) -> str:
        return f"{type(self).__name__}(entity={self.entity} ,out_reg={self.out_reg})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        ent_vdat = get_exec_vdat(self.entity, linker)
        out_vdat = linker.lookup_var(self.out_reg)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Output register does not have linked scoreboard?")
        return [ComCmd(
            f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} " +
            f"run execute if entity {ent_vdat.get_selector(stack_level)}"
        )]


class CmdBlockExists(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "block_exists"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("loc", StructPos.get_type()),
            IParam("required_block", InertType(InertCoreTypes.STR, True))
        ]

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.BOOL)

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        location = param_binding["loc"]
        required_block: str = get_key_with_type(param_binding, "required_block", SmtConstStr).value
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.BOOL))
        return [SmtBlockExistsCmd(location, required_block, output_register)], output_register


class CmdEntityExists(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "entity_exists"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("entity", ExecType(ExecCoreTypes.ENTITY, True))
        ]

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.BOOL)

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        entity = param_binding["entity"]
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.BOOL))
        return [SmtEntityExistsCmd(entity, output_register)], output_register
