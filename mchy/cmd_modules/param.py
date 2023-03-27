from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Collection, Dict, List, Optional, Sequence, Tuple, Union
from mchy.common.abs_ctx import AbsCtxFunc, AbsCtxParam
from mchy.common.com_types import ComType, ExecType, TypeUnion
from mchy.common.config import Config
from mchy.errors import ContextualisationError

if TYPE_CHECKING:
    from mchy.cmd_modules.name_spaces import Namespace
    from mchy.contextual.struct.expr import CtxExprNode
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom


@dataclass(frozen=True)
class IParam:
    label: str
    param_type: Union[ComType, TypeUnion]
    default_ctx_expr: Optional['CtxExprNode'] = None


class CtxIParam(AbsCtxParam):

    def __init__(self, iparam: IParam) -> None:
        self._iparam = iparam

    def get_label(self) -> str:
        return self._iparam.label

    def get_param_type(self) -> Union[ComType, TypeUnion]:
        return self._iparam.param_type

    def is_defaulted(self) -> bool:
        return self._iparam.default_ctx_expr is not None

    def get_default_ctx_expr(self) -> Optional['CtxExprNode']:
        return self._iparam.default_ctx_expr

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._iparam.label}: {self._iparam.param_type.render()}{'' if self._iparam.default_ctx_expr is None else ' = ...'})"
