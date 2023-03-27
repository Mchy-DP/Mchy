from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_key_with_type
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtObjVarLinkage


def validate_tag(tag: str):
    """raises a conversion error if tag is an invalid minecraft tag"""
    if " " in tag:
        raise ConversionError(f"Tags cannot contain space's.  Consider replacing with underscore or dash: (\"{tag}\" -> \"{tag.replace(' ', '_')}\")")


class SmtTagAddCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, new_tag: str) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.new_tag: str = new_tag

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.executor}, new_tag={self.new_tag})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        return [ComCmd(f"tag {exec_vdat.get_selector(stack_level)} add {self.new_tag}")]


class SmtTagRemoveCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, target_tag: str) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.target_tag: str = target_tag

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.executor}, target_tag={self.target_tag})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        return [ComCmd(f"tag {exec_vdat.get_selector(stack_level)} remove {self.target_tag}")]


class SmtTagCountCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, out_reg: SmtVar) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type
        self.out_reg: SmtVar = out_reg

    def __repr__(self) -> str:
        return f"{type(self).__name__}(entity={self.executor}, out_reg={self.out_reg})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        out_vdat = linker.lookup_var(self.out_reg)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Output register does not have linked scoreboard?")
        return [ComCmd(f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run tag {exec_vdat.get_selector(stack_level)} list")]


class CmdTagAdd(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "tag_add"

    def get_params(self) -> Sequence[IParam]:
        return [IParam("new_tag", InertType(InertCoreTypes.STR, True))]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        new_tag: str = get_key_with_type(param_binding, "new_tag", SmtConstStr).value
        validate_tag(new_tag)
        return [SmtTagAddCmd(executor, new_tag)], module.get_null_const()


class CmdTagRemove(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "tag_remove"

    def get_params(self) -> Sequence[IParam]:
        return [IParam("target_tag", InertType(InertCoreTypes.STR, True))]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        tar_tag: str = get_key_with_type(param_binding, "target_tag", SmtConstStr).value
        validate_tag(tar_tag)
        return [SmtTagRemoveCmd(executor, tar_tag)], module.get_null_const()


class CmdTagCount(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, False)

    def get_name(self) -> str:
        return "tag_count"

    def get_params(self) -> Sequence[IParam]:
        return []

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.INT))
        return [SmtTagCountCmd(executor, output_register)], output_register
