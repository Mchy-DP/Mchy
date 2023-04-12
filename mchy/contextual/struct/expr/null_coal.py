
from mchy.common.com_loc import ComLoc
from mchy.errors import ContextualisationError, ConversionError, UnreachableError
from mchy.common.com_types import ComType, ExecType, InertCoreTypes, InertType, StructType

from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.contextual.struct.expr.literals import CtxExprLitNull


class CtxExprNullCoal(CtxExprNode):

    def __init__(self, opt_expr: CtxExprNode, default_expr: CtxExprNode, **kwargs):
        super().__init__([opt_expr, default_expr], src_loc=ComLoc(opt_expr.loc.line, opt_expr.loc.col_start, default_expr.loc.line_end, default_expr.loc.col_end), **kwargs)
        self.opt_expr: CtxExprNode = opt_expr
        self.default_expr: CtxExprNode = default_expr

    def _get_type(self) -> ComType:
        opt_type = self.opt_expr.get_type()
        default_type = self.default_expr.get_type()
        if isinstance(opt_type, StructType):
            raise ConversionError(f"Cannot null coalesce struct-types {opt_type.render()}").with_loc(self.opt_expr.loc)
        elif isinstance(default_type, StructType):
            raise ConversionError(f"Cannot null coalesce struct-types {default_type.render()}").with_loc(self.default_expr.loc)
        elif isinstance(opt_type, ExecType):
            raise ConversionError(f"Cannot null coalesce executable types {opt_type.render()}").with_loc(self.opt_expr.loc)
        elif isinstance(default_type, ExecType):
            raise ConversionError(f"Cannot null coalesce executable types {default_type.render()}").with_loc(self.default_expr.loc)
        elif isinstance(opt_type, InertType) and isinstance(default_type, InertType):
            if default_type.nullable or (default_type.target == InertCoreTypes.NULL):
                raise ConversionError(
                    f"Invalid operation types: Cannot perform Null coalescing with nullable default " +
                    f"`{opt_type.render()}` ?? `{default_type.render()}`"
                )
            match (opt_type, default_type):
                case (InertType(InertCoreTypes.NULL), _):
                    return InertType(default_type.target, (opt_type.const and default_type.const), False)
                case (InertType(InertCoreTypes.STR), InertType(InertCoreTypes.STR)):
                    return InertType(InertCoreTypes.STR, (opt_type.const and default_type.const), False)
                case (
                        (InertType(InertCoreTypes.FLOAT), InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL)) |
                        (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL), InertType(InertCoreTypes.FLOAT))
                        ):
                    return InertType(InertCoreTypes.FLOAT, (opt_type.const and default_type.const), False)
                case (
                        (InertType(InertCoreTypes.INT), InertType(InertCoreTypes.INT | InertCoreTypes.BOOL)) |
                        (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL), InertType(InertCoreTypes.INT))
                        ):
                    return InertType(InertCoreTypes.INT, (opt_type.const and default_type.const), False)
                case (InertType(InertCoreTypes.BOOL), InertType(InertCoreTypes.BOOL)):
                    return InertType(InertCoreTypes.BOOL, (opt_type.const and default_type.const), False)
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot perform null coalescing with types: " +
                        f"`{opt_type.render()}` ?? `{default_type.render()}` ({opt_type.target.value} !~ {default_type.target.value})"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {opt_type.render()} vs {default_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprNullCoal(self.opt_expr.flatten(), self.default_expr.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.opt_expr, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.opt_expr)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.default_expr, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.default_expr)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.opt_expr, CtxExprLitNull):
            return self.default_expr
        else:
            return self.opt_expr
