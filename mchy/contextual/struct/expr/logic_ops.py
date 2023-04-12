
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
            raise ConversionError(f"Cannot 'not' struct-types {target_type.render()}").with_loc(self.target.loc)
        elif isinstance(target_type, ExecType):
            raise ConversionError(f"Cannot 'not' executable types {target_type.render()}").with_loc(self.target.loc)
        elif isinstance(target_type, InertType):
            match (target_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, target_type.const)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot perform boolean 'not' `{self.target.get_type().render()}`").with_loc(self.target.loc)
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
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot 'and' struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot 'and' struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot 'and' executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot 'and' executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot perform boolean 'and' `{self.left.get_type().render()}` and `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
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
        if isinstance(left_type, StructType):
            raise ConversionError(f"Cannot 'or' struct-types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, StructType):
            raise ConversionError(f"Cannot 'or' struct-types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, ExecType):
            raise ConversionError(f"Cannot 'or' executable types {left_type.render()}").with_loc(self.left.loc)
        elif isinstance(right_type, ExecType):
            raise ConversionError(f"Cannot 'or' executable types {right_type.render()}").with_loc(self.right.loc)
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.BOOL, (left_type.const and right_type.const))
                case _:
                    raise ConversionError(
                        f"Invalid operation types: Cannot perform boolean 'or' `{self.left.get_type().render()}` or `{self.right.get_type().render()}`"
                    ).with_loc(self.loc)
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
