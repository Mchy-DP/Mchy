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
from mchy.errors import ConversionError, LibConversionError, StatementRepError, UnreachableError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstInt, SmtConstStr, SmtStruct, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker
from mchy.stmnt.struct.struct import SmtPyStructInstance


class SetblockFlag(enum.Enum):
    REPLACE = "replace"
    DESTROY = "destroy"
    KEEP = "keep"


class SmtSetblockCmd(SmtCmd):

    def __init__(self, location: SmtAtom, block: str, destroy_flag: bool, keep_flag: bool) -> None:
        self.location: SmtAtom = location
        loc_type = self.location.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")
        self.block: str = block
        self.existing_block_behavior: SetblockFlag
        if destroy_flag and keep_flag:
            raise LibConversionError(f"Cannot both keep and destroy existing blocks in setblock ({self.block}@{repr(self.location)})")
        elif destroy_flag and (not keep_flag):
            self.existing_block_behavior = SetblockFlag.DESTROY
        elif (not destroy_flag) and keep_flag:
            self.existing_block_behavior = SetblockFlag.KEEP
        elif (not destroy_flag) and (not keep_flag):
            self.existing_block_behavior = SetblockFlag.REPLACE
        else:
            raise UnreachableError(f"Inconsistent flag state: ({destroy_flag=},{keep_flag=})")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(loc={repr(self.location)}, block={self.block}, mode={self.existing_block_behavior.name})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        pos_str, executor = StructPos.build_position_string(get_struct_instance(self.location), cast_to_int=True)
        cmd = f"setblock {pos_str} {self.block} {self.existing_block_behavior.value}"
        if executor is None:
            return [ComCmd(cmd)]
        else:
            exec_vdat = get_exec_vdat(executor, linker)
            return [ComCmd(f"execute at {exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdSetblock(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "setblock"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("location", StructPos.get_type()),
            IParam("block", InertType(InertCoreTypes.STR, const=True)),
            IParam("mine_existing", InertType(InertCoreTypes.BOOL, const=True), CtxExprLitBool(False, src_loc=ComLoc())),
            IParam("keep_existing", InertType(InertCoreTypes.BOOL, const=True), CtxExprLitBool(False, src_loc=ComLoc())),
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        location = param_binding["location"]
        block = get_key_with_type(param_binding, "block", SmtConstStr).value
        destroy_flag = (get_key_with_type(param_binding, "mine_existing", SmtConstInt).value >= 1)
        keep_flag = (get_key_with_type(param_binding, "keep_existing", SmtConstInt).value >= 1)
        return [SmtSetblockCmd(location, block, destroy_flag, keep_flag)], module.get_null_const()
