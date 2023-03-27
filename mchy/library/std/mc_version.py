
from typing import List, Tuple
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.properties import IProp
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom


class PropMinecraftVersion(IProp):  # FIXME: TODO: Depreciated remove when other properties have been added to std library

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "version"

    def get_prop_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)

    def stmnt_conv(self, executor: SmtAtom, module: SmtModule, function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
        return [], module.get_const_with_val(-1)  # -1 as not implemented yet
