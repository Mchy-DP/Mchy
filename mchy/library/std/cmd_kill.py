from typing import Collection, Dict, List, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtKillCmd(SmtCmd):

    def __init__(self, executor: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self._exec_type: ExecType = exec_type

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.executor})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        if not isinstance(self.executor, SmtVar):
            raise VirtualRepError(f"Unhandled atom type {type(self.executor).__name__}")
        exec_vdat = linker.lookup_var(self.executor)
        if not isinstance(exec_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor variable data for `{repr(self.executor)}` does not include tag despite being of executable type?")
        return [ComCmd(f"kill {exec_vdat.get_selector(stack_level)}")]


class CmdKill(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "kill"

    def get_params(self) -> Sequence[IParam]:
        return []

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config, loc: ComLoc
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        return [SmtKillCmd(executor)], module.get_null_const()
