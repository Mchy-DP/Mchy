import enum
from typing import Collection, Dict, List, Optional, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitFloat, CtxExprLitNull
from mchy.errors import ConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker
from mchy.stmnt.struct.struct import SmtPyStructInstance


class SmtSpreadPlayersCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, center: SmtAtom, radius: float, spacing: float, respect_teams: bool, max_height: Optional[int]) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.center: SmtAtom = center
        loc_type = self.center.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")
        self.radius: float = radius
        self.spacing: float = spacing
        self.respect_teams: bool = respect_teams
        self.max_height: Optional[int] = max_height

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(exec={repr(self.executor)}, center={repr(self.center)}, radius={self.radius}, " +
            f"spacing={self.spacing}, respect_teams={self.respect_teams}, max_height={self.max_height})"
        )

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, location_executor = StructPos.build_position_string(get_struct_instance(self.center), suppress_y_coord=True)
        # solve target
        if self._exec_type.target == ExecCoreTypes.WORLD:
            raise VirtualRepError("Attempted to spread the world despite passing earlier type check")
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        as_exec_vdat = get_exec_vdat(self.executor, linker)
        target_selector: str = f"{as_exec_vdat.get_selector(stack_level)}"

        # generate command
        cmd = (
            f"spreadplayers {pos_str} {self.spacing} {self.radius} {('' if self.max_height is None else f'under {self.max_height}')}" +
            f"{'false' if self.respect_teams is False else 'true'} {target_selector}")

        # return command
        if location_executor is None:
            return [ComCmd(cmd)]
        else:
            at_exec_vdat = get_exec_vdat(location_executor, linker)
            return [ComCmd(f"execute at {at_exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdSpread(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "spread"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("center", StructPos.get_type()),
            IParam("radius", InertType(InertCoreTypes.FLOAT, const=True)),
            IParam("spacing", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitFloat(0.0, src_loc=ComLoc())),
            IParam("respect_teams", InertType(InertCoreTypes.BOOL, const=True), CtxExprLitBool(False, src_loc=ComLoc())),
            IParam("max_height", InertType(InertCoreTypes.INT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        center = param_binding["center"]
        radius = get_key_with_type(param_binding, "radius", SmtConstFloat).value
        spacing = get_key_with_type(param_binding, "spacing", SmtConstFloat).value
        respect_teams = (get_key_with_type(param_binding, "respect_teams", SmtConstInt).value >= 1)
        max_height: Optional[int] = None
        try:
            max_height = get_key_with_type(param_binding, "max_height", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "max_height", SmtConstNull)
        return [SmtSpreadPlayersCmd(executor, center, radius, spacing, respect_teams, max_height)], module.get_null_const()
