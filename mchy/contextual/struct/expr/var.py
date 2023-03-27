from mchy.contextual.struct.expr.structs import CtxExprPyStruct, CtxPyStructInstance
from mchy.errors import ContextualisationError
from mchy.common.com_types import ComType, StructType
from mchy.contextual.struct.var_scope import CtxVar
from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits


class CtxExprVar(CtxExprNode):

    def __init__(self, var: 'CtxVar', **kwargs):
        super().__init__([], **kwargs)
        self.var: CtxVar = var

    def _get_type(self) -> ComType:
        return self.var.var_type

    def _flatten_children(self) -> 'CtxExprNode':
        if isinstance(self.get_type(), StructType):
            if self.var.declaration_marker.default_assignment is None:
                raise ContextualisationError(f"Struct variable has no assignment")
            if not isinstance(self.var.declaration_marker.default_assignment.rhs, CtxExprPyStruct):
                raise ContextualisationError(f"Struct variable is not assigned to a valid struct, found: {repr(self.var.declaration_marker.default_assignment.rhs)}")
            return CtxExprPyStruct(
                self.var.declaration_marker.default_assignment.rhs.struct_instance.struct,
                self.var.declaration_marker.default_assignment.rhs.struct_instance.creation_field_binding(),
                src_loc=self.loc
            )
        return self

    def _flatten_body(self) -> 'CtxExprLits':
        if self.var.declaration_marker.default_assignment is None:
            raise ContextualisationError(f"Compile const variable has no assignment")
        if not isinstance(self.var.declaration_marker.default_assignment.rhs, CtxExprLits):
            # Due to the flatten call in convert_expr it should be impossible to create something that fails this check
            raise ContextualisationError(f"Compile const variable is not assigned to a literal")
        return self.var.declaration_marker.default_assignment.rhs  # Replace this variable node with it's literal value from the assignment

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprVar) and self.var == other.var

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.var.render()})'
