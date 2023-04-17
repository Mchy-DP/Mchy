
from typing import Any
from mchy.common.com_loc import ComLoc

from mchy.errors import ContextualisationError, ConversionError, UnreachableError
from mchy.common.com_types import ComType, ExecType, InertCoreTypes, InertType, StructType
from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitFloat, CtxExprLitInt, CtxExprLitStr, CtxExprLitNull


class CtxExprCompEquality(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        # Equality is only valid on floats and strings at compile time
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot test equality on struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot test equality on struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot test equality on executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot test equality on executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            if left_type.const and right_type.const:
                return InertType(InertCoreTypes.BOOL, True)  # Constant calculations can always happen
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL | InertCoreTypes.NULL),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL | InertCoreTypes.NULL)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))  # Run-time bool & int calculations can happen
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot test equality between `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprCompEquality(self.left.flatten(), self.right.flatten())

    @staticmethod
    def get_bflat_bool(caller: Any, left: CtxExprNode, right: CtxExprNode) -> bool:
        if not isinstance(left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(left)}) of flattened `{type(caller).__name__}` encountered")
        if not isinstance(right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(right)}) of flattened `{type(caller).__name__}` encountered")

        left_type = left.get_type()
        right_type = right.get_type()
        if (not isinstance(left_type, InertType)) or (not isinstance(right_type, InertType)):
            raise ContextualisationError(f"Non-inert type encountered during flattening (`{left_type}` & `{right_type}`)")
        if isinstance(left, CtxExprLitNull) and isinstance(right, CtxExprLitNull):
            return True
        if isinstance(left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(right, (CtxExprLitInt, CtxExprLitBool)):
            return int(left.value) == int(right.value)
        if (isinstance(left, (CtxExprLitInt, CtxExprLitBool, CtxExprLitFloat, CtxExprLitStr)) and
                isinstance(right, (CtxExprLitInt, CtxExprLitBool, CtxExprLitFloat, CtxExprLitStr))):
            return ((left_type == right_type) and (left.value == right.value))
        return ((left_type == right_type) and (left == right))

    def _flatten_body(self) -> 'CtxExprLits':
        return CtxExprLitBool(CtxExprCompEquality.get_bflat_bool(self, self.left, self.right), src_loc=self.loc)


class CtxExprCompGTE(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot test >= on struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot test >= on struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot test >= on executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot test >= on executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, const=True, nullable=False)
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot test >= of `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprCompGTE(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(int(self.left.value) >= int(self.right.value)), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(float(self.left.value) >= float(self.right.value)), src_loc=self.loc)
        else:
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{self.get_type()}`")


class CtxExprCompGT(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot test > on struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot test > on struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot test > on executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot test > on executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, const=True, nullable=False)
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot test > of `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprCompGT(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(int(self.left.value) > int(self.right.value)), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(float(self.left.value) > float(self.right.value)), src_loc=self.loc)
        else:
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{self.get_type()}`")


class CtxExprCompLTE(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot test <= on struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot test <= on struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot test <= on executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot test <= on executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, const=True, nullable=False)
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot test <= of `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprCompLTE(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(int(self.left.value) <= int(self.right.value)), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(float(self.left.value) <= float(self.right.value)), src_loc=self.loc)
        else:
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{self.get_type()}`")


class CtxExprCompLT(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot test < on struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot test < on struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot test < on executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot test < on executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, const=True, nullable=False)
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot test < of `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprCompLT(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(int(self.left.value) < int(self.right.value)), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitBool(bool(float(self.left.value) < float(self.right.value)), src_loc=self.loc)
        else:
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{self.get_type()}`")
