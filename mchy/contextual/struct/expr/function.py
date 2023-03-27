
from typing import Dict, List, Optional, Union

from mchy.common.abs_ctx import AbsCtxFunc, AbsCtxParam
from mchy.common.com_types import ComType, TypeUnion
from mchy.contextual.struct.expr.abs_node import CtxExprLits, CtxExprNode
from mchy.errors import UnreachableError


class CtxExprFuncCall(CtxExprNode):

    def __init__(self, executor: CtxExprNode, function: AbsCtxFunc, param_values: List['CtxExprParamVal'], extra_pvals: List['CtxExprExtraParamVal'] = [], **kwargs):
        children: List[CtxExprNode] = [executor]
        children.extend(param_values)
        children.extend(extra_pvals)
        super().__init__(children, **kwargs)
        self.executor: CtxExprNode = executor
        self.function: AbsCtxFunc = function
        self._param_values: List['CtxExprParamVal'] = param_values
        self._extra_values: List['CtxExprExtraParamVal'] = extra_pvals
        self._param_lookup: Dict[AbsCtxParam, Optional[CtxExprNode]] = {param.param: param.value for param in self._param_values}

    def get_extra_values(self) -> List[CtxExprNode]:
        return [extra_val.value for extra_val in self._extra_values]

    def get_param_value(self, param: AbsCtxParam) -> Optional[CtxExprNode]:
        return self._param_lookup[param]

    def _get_type(self) -> ComType:
        return self.function.get_return_type()

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprFuncCall(self.executor.flatten(), self.function, [p.flatten() for p in self._param_values], [p.flatten() for p in self._extra_values], src_loc=self.loc)

    def _flatten_body(self) -> 'CtxExprLits':
        raise ValueError(f"Function calls are unflattenable")

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprFuncCall) and self.function == other.function

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f", function='{self.function.get_name()}'" + ")"


class CtxExprParamVal(CtxExprNode):

    def __init__(self, param: AbsCtxParam, value: Optional[CtxExprNode], **kwargs):
        super().__init__([], **kwargs)
        self.param: AbsCtxParam = param
        self.value: Optional[CtxExprNode] = value

    def _get_type(self) -> ComType:
        raise UnreachableError(f"The type of a param binding should never be queried")

    def flatten(self) -> 'CtxExprParamVal':
        return CtxExprParamVal(self.param, (self.value.flatten() if self.value is not None else None), src_loc=self.loc)

    def _flatten_children(self) -> 'CtxExprNode':
        raise UnreachableError(f"Param's do not use standard flatten methods")

    def _flatten_body(self) -> 'CtxExprLits':
        raise UnreachableError(f"Param's do not use standard flatten methods")

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprParamVal) and self.param == other.param and self.value == other.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.param.get_label()}: {self.param.get_param_type()} = {(self.value if self.value is not None else 'DEFAULT')})"


class CtxExprExtraParamVal(CtxExprNode):

    def __init__(self, ptype: Union[ComType, TypeUnion], value: CtxExprNode, **kwargs):
        super().__init__([], **kwargs)
        self.ptype: Union[ComType, TypeUnion] = ptype
        self.value: CtxExprNode = value

    def _get_type(self) -> ComType:
        raise UnreachableError(f"The type of a param binding should never be queried")

    def flatten(self) -> 'CtxExprExtraParamVal':
        return CtxExprExtraParamVal(self.ptype, self.value.flatten(), src_loc=self.loc)

    def _flatten_children(self) -> 'CtxExprNode':
        raise UnreachableError(f"Param's do not use standard flatten methods")

    def _flatten_body(self) -> 'CtxExprLits':
        raise UnreachableError(f"Param's do not use standard flatten methods")

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprExtraParamVal) and self.ptype == other.ptype and self.value == other.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(*: {self.ptype} = {self.value})"
