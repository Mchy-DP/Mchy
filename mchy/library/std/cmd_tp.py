from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtTpCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, target_location: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.target_location: SmtAtom = target_location
        loc_type = self.target_location.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(who={self.executor}, where={self.target_location})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, location_executor = StructPos.build_position_string(get_struct_instance(self.target_location))
        # solve sound location
        if self._exec_type.target == ExecCoreTypes.WORLD:
            raise VirtualRepError("Attempted to tp the world despite passing earlier type check")
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        as_exec_vdat = get_exec_vdat(self.executor, linker)
        effected_entities: str = f"{as_exec_vdat.get_selector(stack_level)}"

        # generate command
        cmd = f"tp {effected_entities} {pos_str}"

        # return command
        if location_executor is None:
            return [ComCmd(cmd)]
        else:
            at_exec_vdat = get_exec_vdat(location_executor, linker)
            if not at_exec_vdat.solitary:
                raise ConversionError("`tp` called with Group of target positions, cannot teleport entity to multiple places?")
            return [ComCmd(f"execute at {at_exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdTp(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "tp"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("target_location", StructPos.get_type()),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config, loc: ComLoc
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        target_location = param_binding["target_location"]
        return [SmtTpCmd(executor, target_location)], module.get_null_const()
