from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.common.com_types import ExecCoreTypes, ExecType, InertCoreTypes, InertType


class CtxExprLitStr(CtxExprLits):

    def __init__(self, value: str, **kwargs):
        super().__init__([], **kwargs)
        self.value: str = value

    def _get_type(self) -> InertType:
        return InertType(InertCoreTypes.STR, True, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprLitStr) and self.value == other.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}("{self.value}")'


class CtxExprLitInt(CtxExprLits):

    def __init__(self, value: int, **kwargs):
        super().__init__([], **kwargs)
        self.value: int = value

    def _get_type(self) -> InertType:
        return InertType(InertCoreTypes.INT, True, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprLitInt) and self.value == other.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value})'


class CtxExprLitFloat(CtxExprLits):

    def __init__(self, value: float, **kwargs):
        super().__init__([], **kwargs)
        self.value: float = value

    def _get_type(self) -> InertType:
        return InertType(InertCoreTypes.FLOAT, True, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprLitFloat) and self.value == other.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value})'


class CtxExprLitNull(CtxExprLits):

    def __init__(self, **kwargs):
        super().__init__([], **kwargs)

    def _get_type(self) -> InertType:
        return InertType(InertCoreTypes.NULL, True, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __repr__(self) -> str:
        return f'{type(self).__name__}()'


class CtxExprLitWorld(CtxExprLits):

    def __init__(self, **kwargs):
        super().__init__([], **kwargs)

    def _get_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __repr__(self) -> str:
        return f'{type(self).__name__}()'


class CtxExprLitThis(CtxExprLits):

    def __init__(self, this_type: ExecType, **kwargs):
        super().__init__([], **kwargs)
        self._this_type = this_type

    def _get_type(self) -> ExecType:
        return self._this_type

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprLitThis) and self._this_type == other._this_type

    def __repr__(self) -> str:
        return f'{type(self).__name__}(type={self._this_type.render()})'


class CtxExprLitBool(CtxExprLits):

    def __init__(self, value: bool, **kwargs):
        super().__init__([], **kwargs)
        self.value: bool = value

    def _get_type(self) -> InertType:
        return InertType(InertCoreTypes.BOOL, True, False)

    def _flatten_children(self) -> 'CtxExprNode':
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        return self  # Shouldn't be called but no harm done by calling it

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprLitBool) and self.value == other.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value})'
