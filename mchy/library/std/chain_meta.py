import datetime
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import CtxExprLitStr, CtxExprLits, CtxExprNode, CtxChainLink
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule


class ChainLinkMeta(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "meta"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainMetaCompileTime(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkMeta

    def get_name(self) -> str:
        return "compile_time"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def get_chain_type(self) -> ComType:
        return InertType(InertCoreTypes.STR, const=True)

    def yield_const_value(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink']) -> 'CtxExprLits':
        return CtxExprLitStr(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), src_loc=ComLoc())
