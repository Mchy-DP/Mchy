from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitStr
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstInt, SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtGiveCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, item: str, count: int, data: str) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self.item: str = item
        self.count: int = count
        self.data: str = data

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={self.executor}, item={self.item}, count={self.count}, data={self.data})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        return [ComCmd(f"give {exec_vdat.get_selector()} {self.item}{self.data} {self.count}")]


class CmdGive(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.PLAYER, True)

    def get_name(self) -> str:
        return "give"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("item", InertType(InertCoreTypes.STR, const=True)),
            IParam("count", InertType(InertCoreTypes.INT, const=True)),  # binary search to allow arbitrary int
            IParam("data", InertType(InertCoreTypes.STR, const=True), CtxExprLitStr(r"{}", src_loc=ComLoc()))
        ]

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.PLAYER, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on players, not `{executor.get_type().render()}`")
        item: str = get_key_with_type(param_binding, "item", SmtConstStr).value
        count: int = get_key_with_type(param_binding, "count", SmtConstInt).value
        data: str = get_key_with_type(param_binding, "data", SmtConstStr).value
        if count < 1:
            raise ConversionError(f"Give count cannot be less than 1")
        if count > 6400:
            # TODO: consider generating multiple give statements so any upper bound is ok -> emit warning if number big though
            raise ConversionError(f"Give count cannot be more than 6400")
        return [SmtGiveCmd(executor, item, count, data)], module.get_null_const()
