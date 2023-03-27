
from mchy.common.com_loc import ComLoc
from mchy.errors import ContextualisationError, ConversionError, UnreachableError
from mchy.common.com_types import ComType, ExecType, InertCoreTypes, InertType, StructType

from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.contextual.struct.expr.literals import CtxExprLitBool


class CtxExprNot(CtxExprNode):

    def __init__(self, target: CtxExprNode, **kwargs):
        super().__init__([target], src_loc=target.loc, **kwargs)
        self.target: CtxExprNode = target

    def _get_type(self) -> ComType:
        target_type = self.target.get_type()
        if isinstance(target_type, StructType):
            raise ConversionError(f"StructTypes are not valid in boolean NOT operations")
        elif isinstance(target_type, ExecType):
            raise ConversionError("Boolean 'Not' of Executable types is not supported")
        elif isinstance(target_type, InertType):
            match (target_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, target_type.const)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot perform boolean 'Not' `{self.target.get_type().render()}`")
        else:
            raise UnreachableError(f"Type unexpectedly did not match any option {target_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprNot(self.target.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.target, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.target)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.target, CtxExprLitBool):
            return CtxExprLitBool((not self.target.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprAnd(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType) or isinstance(right_type, StructType):
            raise ConversionError(f"StructTypes are not valid in boolean AND operations")
        elif isinstance(left_type, ExecType) and isinstance(right_type, ExecType):
            raise ConversionError("Boolean 'And' of Executable types is not supported")
        elif (isinstance(left_type, ExecType) and isinstance(right_type, InertType)) or (isinstance(left_type, InertType) and isinstance(right_type, ExecType)):
            raise ConversionError("Cannot perform boolean 'And' inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot perform boolean 'And' `{self.left.get_type().render()}` and `{self.right.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprAnd(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, CtxExprLitBool) and isinstance(self.right, CtxExprLitBool):
            return CtxExprLitBool((self.left.value and self.right.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprOr(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType) or isinstance(right_type, StructType):
            raise ConversionError(f"StructTypes are not valid in boolean OR operations")
        elif isinstance(left_type, ExecType) and isinstance(right_type, ExecType):
            raise ConversionError("Boolean 'Or' of Executable types is not supported")
        elif (isinstance(left_type, ExecType) and isinstance(right_type, InertType)) or (isinstance(left_type, InertType) and isinstance(right_type, ExecType)):
            raise ConversionError("Cannot perform boolean 'Or' inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot perform boolean 'Or' `{self.left.get_type().render()}` or `{self.right.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprOr(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, CtxExprLitBool) and isinstance(self.right, CtxExprLitBool):
            return CtxExprLitBool((self.left.value or self.right.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")
