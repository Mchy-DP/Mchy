import json
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Union

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_key_with_type
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, TypeUnion, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitNull
from mchy.errors import ConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_color import StructColor
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar, SmtWorld
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtObjVarLinkage, SmtVarLinkage


class SmtEffectCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, effect: str, seconds: int, amp: int, particles: bool) -> None:
        self.executor: SmtAtom = executor
        _exec_type = self.executor.get_type()
        if not isinstance(_exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {_exec_type}, ExecType required")
        self.effect: str = effect
        self.seconds: int = seconds
        self.amp: int = amp
        self.particles: bool = particles

    def __repr__(self) -> str:
        return f"{type(self).__name__}(exec={self.executor}, effect={self.effect}, duration={self.seconds}s, amplifier={self.amp}, particles={self.particles})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        # Get exec data:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        # return command
        return [ComCmd(f"effect give {exec_vdat.get_selector(stack_level)} {self.effect} {self.seconds} {self.amp} {('true' if self.particles else 'false')}")]


class SmtClearEffectCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, effect: Optional[str]) -> None:
        self.executor: SmtAtom = executor
        _exec_type = self.executor.get_type()
        if not isinstance(_exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {_exec_type}, ExecType required")
        self.effect: Optional[str] = effect

    def __repr__(self) -> str:
        return f"{type(self).__name__}(exec={self.executor}, effect={self.effect})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        # Get exec data:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        # return command
        return [ComCmd(f"effect clear {exec_vdat.get_selector(stack_level)} {('' if self.effect is None else self.effect)}")]


class CmdEffectAdd(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "effect_add"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("effect", InertType(InertCoreTypes.STR, True)),
            IParam("seconds", InertType(InertCoreTypes.INT, True)),
            IParam("amplifier", InertType(InertCoreTypes.INT, True)),
            IParam("particles", InertType(InertCoreTypes.BOOL, True), CtxExprLitBool(True, src_loc=ComLoc()))
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        # get fields
        effect = get_key_with_type(param_binding, "effect", SmtConstStr).value  # TODO: emit warning if effect is not recognized
        seconds = get_key_with_type(param_binding, "seconds", SmtConstInt).value
        amp = get_key_with_type(param_binding, "amplifier", SmtConstInt).value
        particles = (get_key_with_type(param_binding, "particles", SmtConstInt).value >= 1)
        # validation
        if seconds <= 0:
            raise ConversionError(f"Effect amplitude must be greater than 0 (found: {amp})")
        if amp < 0:
            raise ConversionError(f"Effect amplitude cannot be negative (found: {amp})")
        # build and return statements
        return [SmtEffectCmd(executor, effect, seconds, amp, particles)], module.get_null_const()


class CmdEffectClear(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "effect_clear"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("effect", InertType(InertCoreTypes.STR, True, True), CtxExprLitNull(src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        # get fields
        effect_param = param_binding["effect"]
        if isinstance(effect_param, SmtConstNull):
            effect = None
        elif isinstance(effect_param, SmtConstStr):
            effect = effect_param.value  # TODO: emit warning if effect is not recognized
        # build and return statements
        return [SmtClearEffectCmd(executor, effect)], module.get_null_const()
