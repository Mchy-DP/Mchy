import json
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Union

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, TypeUnion, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitNull
from mchy.errors import ConversionError, LibConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.cmd_setblock import SetblockFlag
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_color import StructColor
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar, SmtWorld
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtObjVarLinkage, SmtVarLinkage


class SmtFillCmd(SmtCmd):

    def __init__(self, pos1: SmtAtom, pos2: SmtAtom, block: str, destroy_flag: bool, keep_flag: bool) -> None:
        self.pos1: SmtAtom = pos1
        pos1_type = self.pos1.get_type()
        if pos1_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with pos1 of type {pos1_type.render()}, {StructPos.get_type().render()} required")
        self.pos2: SmtAtom = pos2
        pos2_type = self.pos2.get_type()
        if pos2_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with pos2 of type {pos2_type.render()}, {StructPos.get_type().render()} required")
        self.block: str = block
        self.existing_block_behavior: SetblockFlag
        if destroy_flag and keep_flag:
            raise LibConversionError(f"Cannot both keep and destroy existing blocks in fill ({self.block}@{repr(self.pos1)}-{repr(self.pos2)})")
        elif destroy_flag and (not keep_flag):
            self.existing_block_behavior = SetblockFlag.DESTROY
        elif (not destroy_flag) and keep_flag:
            self.existing_block_behavior = SetblockFlag.KEEP
        elif (not destroy_flag) and (not keep_flag):
            self.existing_block_behavior = SetblockFlag.REPLACE
        else:
            raise UnreachableError(f"Inconsistent flag state: ({destroy_flag=},{keep_flag=})")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(pos1={repr(self.pos1)}, pos2={repr(self.pos2)}, block={self.block}, mode={self.existing_block_behavior.name})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos1_str, executor1 = StructPos.build_position_string(get_struct_instance(self.pos1))
        pos2_str, executor2 = StructPos.build_position_string(get_struct_instance(self.pos2))
        # resolve executor
        executor: Optional[SmtAtom]
        if (executor1 is None) and (executor2 is None):
            executor = None
        elif (executor1 is not None) and (executor2 is None):
            executor = executor1
        elif (executor1 is None) and (executor2 is not None):
            executor = executor2
        elif (executor1 is not None) and (executor2 is not None):
            exec1_vdat = get_exec_vdat(executor1, linker)
            exec2_vdat = get_exec_vdat(executor2, linker)
            if exec1_vdat.get_selector(stack_level) == exec2_vdat.get_selector(stack_level):
                executor = executor1
            else:
                raise LibConversionError("If 'pos1' and 'pos2' are both positioned relative to an entity it must be the same entity (Blame minecraft)")
        # build fill command
        cmd = f"fill {pos1_str} {pos2_str} {self.block} {self.existing_block_behavior.value}"
        # return command
        if executor is None:
            return [ComCmd(cmd)]
        else:
            exec_vdat = get_exec_vdat(executor, linker)
            return [ComCmd(f"execute at {exec_vdat.get_selector(stack_level)} run {cmd}")]


class SmtFillReplaceCmd(SmtCmd):

    def __init__(self, pos1: SmtAtom, pos2: SmtAtom, old_block: str, new_block: str) -> None:
        self.pos1: SmtAtom = pos1
        pos1_type = self.pos1.get_type()
        if pos1_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with pos1 of type {pos1_type.render()}, {StructPos.get_type().render()} required")
        self.pos2: SmtAtom = pos2
        pos2_type = self.pos2.get_type()
        if pos2_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with pos2 of type {pos2_type.render()}, {StructPos.get_type().render()} required")
        self.old_block: str = old_block
        self.new_block: str = new_block

    def __repr__(self) -> str:
        return f"{type(self).__name__}(pos1={repr(self.pos1)}, pos2={repr(self.pos2)}, old_block={self.old_block}, new_block={self.new_block})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos1_str, executor1 = StructPos.build_position_string(get_struct_instance(self.pos1))
        pos2_str, executor2 = StructPos.build_position_string(get_struct_instance(self.pos2))
        # resolve executor
        executor: Optional[SmtAtom]
        if (executor1 is None) and (executor2 is None):
            executor = None
        elif (executor1 is not None) and (executor2 is None):
            executor = executor1
        elif (executor1 is None) and (executor2 is not None):
            executor = executor2
        elif (executor1 is not None) and (executor2 is not None):
            exec1_vdat = get_exec_vdat(executor1, linker)
            exec2_vdat = get_exec_vdat(executor2, linker)
            if exec1_vdat.get_selector(stack_level) == exec2_vdat.get_selector(stack_level):
                executor = executor1
            else:
                raise LibConversionError("If 'pos1' and 'pos2' are both positioned relative to an entity it must be the same entity (Blame minecraft)")
        # build fill command
        cmd = f"fill {pos1_str} {pos2_str} {self.new_block} replace {self.old_block}"
        # return command
        if executor is None:
            return [ComCmd(cmd)]
        else:
            exec_vdat = get_exec_vdat(executor, linker)
            return [ComCmd(f"execute at {exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdFill(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "fill"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("pos1", StructPos.get_type()),
            IParam("pos2", StructPos.get_type()),
            IParam("block", InertType(InertCoreTypes.STR, True)),
            IParam("mine_existing", InertType(InertCoreTypes.BOOL, const=True), CtxExprLitBool(False, src_loc=ComLoc())),
            IParam("keep_existing", InertType(InertCoreTypes.BOOL, const=True), CtxExprLitBool(False, src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config, loc: ComLoc
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        # get fields
        pos1 = param_binding["pos1"]
        pos2 = param_binding["pos2"]
        block = get_key_with_type(param_binding, "block", SmtConstStr).value
        destroy_flag = (get_key_with_type(param_binding, "mine_existing", SmtConstInt).value >= 1)
        keep_flag = (get_key_with_type(param_binding, "keep_existing", SmtConstInt).value >= 1)
        return [SmtFillCmd(pos1, pos2, block, destroy_flag, keep_flag)], module.get_null_const()


class CmdAreaReplace(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "area_replace"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("pos1", StructPos.get_type()),
            IParam("pos2", StructPos.get_type()),
            IParam("old_block", InertType(InertCoreTypes.STR, True)),
            IParam("new_block", InertType(InertCoreTypes.STR, True)),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config, loc: ComLoc
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        # get fields
        pos1 = param_binding["pos1"]
        pos2 = param_binding["pos2"]
        old = get_key_with_type(param_binding, "old_block", SmtConstStr).value
        new = get_key_with_type(param_binding, "new_block", SmtConstStr).value
        return [SmtFillReplaceCmd(pos1, pos2, old, new)], module.get_null_const()
