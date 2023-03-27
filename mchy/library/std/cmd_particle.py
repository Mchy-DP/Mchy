import enum
from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitBool
from mchy.errors import ConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstStr
from mchy.stmnt.struct.linker import SmtLinker


class SmtParticleCmd(SmtCmd):

    def __init__(self, particle: str, location: SmtAtom, dx: float, dy: float, dz: float, speed: float, count: int, force_render: bool) -> None:
        self.particle: str = particle
        self.location: SmtAtom = location
        loc_type = self.location.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")
        self.dx: float = dx
        self.dy: float = dy
        self.dz: float = dz
        self.speed: float = speed
        self.count: int = count
        self.force_render: bool = force_render

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(loc={repr(self.location)}, particle={self.particle}, dx={self.dx}, dy={self.dy}, dz={self.dz}," +
            f" speed={self.speed}, count={self.count}, force={self.force_render})"
        )

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, executor = StructPos.build_position_string(get_struct_instance(self.location))
        cmd = (
            f"particle {self.particle} {pos_str} {round(self.dx, 4)} {round(self.dy, 4)} {round(self.dz, 4)} {round(self.speed, 4)} {self.count}" +
            (" force" if self.force_render else " normal")
        )
        if executor is None:
            return [ComCmd(cmd)]
        else:
            exec_vdat = get_exec_vdat(executor, linker)
            return [ComCmd(f"execute at {exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdParticle(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "particle"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("location", StructPos.get_type()),
            IParam("particle", InertType(InertCoreTypes.STR, True)),
            IParam("dx", InertType(InertCoreTypes.FLOAT, True)),
            IParam("dy", InertType(InertCoreTypes.FLOAT, True)),
            IParam("dz", InertType(InertCoreTypes.FLOAT, True)),
            IParam("speed", InertType(InertCoreTypes.FLOAT, True)),
            IParam("count", InertType(InertCoreTypes.INT, True)),
            IParam("force_render", InertType(InertCoreTypes.BOOL, True), CtxExprLitBool(False, src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        location = param_binding["location"]
        particle = get_key_with_type(param_binding, "particle", SmtConstStr).value
        dx = get_key_with_type(param_binding, "dx", SmtConstFloat).value
        dy = get_key_with_type(param_binding, "dy", SmtConstFloat).value
        dz = get_key_with_type(param_binding, "dz", SmtConstFloat).value
        speed = get_key_with_type(param_binding, "speed", SmtConstFloat).value
        count = get_key_with_type(param_binding, "count", SmtConstInt).value
        force_render = (get_key_with_type(param_binding, "force_render", SmtConstInt).value >= 1)
        return [SmtParticleCmd(particle, location, dx, dy, dz, speed, count, force_render)], module.get_null_const()
