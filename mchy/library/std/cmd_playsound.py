
import enum
from typing import Collection, Dict, List, Optional, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitFloat, CtxExprLitNull, CtxExprLitStr
from mchy.errors import ConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker
from mchy.stmnt.struct.struct import SmtPyStructInstance


class SmtPlaySoundCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, sound_location: SmtAtom, channel: str, sound: str, volume: float, pitch: float, min_volume: float) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.sound_location: SmtAtom = sound_location
        loc_type = self.sound_location.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")
        self.channel: str = channel
        self.sound: str = sound
        self.volume: float = volume
        self.pitch: float = pitch
        self.min_volume: float = min_volume

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(exec={repr(self.executor)}, sound_loc={repr(self.sound_location)}, sound={self.sound}, " +
            f"channel={self.channel}, volume={self.volume}, pitch={self.pitch}, min_volume={self.min_volume})"
        )

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, location_executor = StructPos.build_position_string(get_struct_instance(self.sound_location))
        # solve sound location
        if self._exec_type.target == ExecCoreTypes.WORLD:
            raise VirtualRepError("Attempted to spread the world despite passing earlier type check")
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        as_exec_vdat = get_exec_vdat(self.executor, linker)
        player_sound_target_selector: str = f"{as_exec_vdat.get_selector(stack_level)}"

        # generate command
        cmd = f"playsound {self.sound} {self.channel} {player_sound_target_selector} {pos_str} {self.volume} {self.pitch} {self.min_volume}"

        # return command
        if location_executor is None:
            return [ComCmd(cmd)]
        else:
            at_exec_vdat = get_exec_vdat(location_executor, linker)
            return [ComCmd(f"execute at {at_exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdPlaySound(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.PLAYER, True)

    def get_name(self) -> str:
        return "play_sound"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("sound_location", StructPos.get_type()),
            IParam("sound", InertType(InertCoreTypes.STR, const=True)),
            IParam("channel", InertType(InertCoreTypes.STR, const=True), CtxExprLitStr("master", src_loc=ComLoc())),
            IParam("volume", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitFloat(1.0, src_loc=ComLoc())),
            IParam("pitch", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitFloat(1.0, src_loc=ComLoc())),
            IParam("min_volume", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitFloat(0.0, src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        sound_location = param_binding["sound_location"]
        channel = get_key_with_type(param_binding, "channel", SmtConstStr).value
        sound = get_key_with_type(param_binding, "sound", SmtConstStr).value
        volume = get_key_with_type(param_binding, "volume", SmtConstFloat).value
        pitch = get_key_with_type(param_binding, "pitch", SmtConstFloat).value
        min_volume = get_key_with_type(param_binding, "min_volume", SmtConstFloat).value
        return [SmtPlaySoundCmd(executor, sound_location, channel, sound, volume, pitch, min_volume)], module.get_null_const()
