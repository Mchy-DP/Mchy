
from mchy.common.com_loc import ComLoc
from mchy.contextual.struct import ComType, CtxExprNode
from mchy.contextual.struct.expr import CtxExprLits
from mchy.errors import UnreachableError


class CtxTTypeNode(CtxExprNode):

    def __init__(self, yielding_type: ComType):
        super().__init__([], src_loc=ComLoc())
        self.yielding_type: ComType = yielding_type

    def _get_type(self) -> ComType:
        return self.yielding_type

    def _flatten_children(self) -> 'CtxExprLits':
        raise UnreachableError()

    def _flatten_body(self) -> 'CtxExprLits':
        raise UnreachableError()
