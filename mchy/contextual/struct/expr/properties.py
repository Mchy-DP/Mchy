
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType
from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.cmd_modules.properties import IProp


class CtxExprPropertyAccess(CtxExprNode):

    def __init__(self, source: CtxExprNode, prop: IProp, **kwargs):
        super().__init__([source], **kwargs)
        self.source: CtxExprNode = source
        self.prop: IProp = prop

    def _get_type(self) -> ComType:
        return self.prop.get_prop_type()

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprPropertyAccess(self.source.flatten(), self.prop)

    def _flatten_body(self) -> 'CtxExprLits':
        raise ValueError("Cannot flatten property access")

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprPropertyAccess) and self.prop.get_name() == other.prop.get_name()

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f", property_name='{self.prop.get_name()}'" + ")"
