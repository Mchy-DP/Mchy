
from mchy.common.com_loc import ComLoc
from mchy.errors import ContextualisationError, ConversionError, UnreachableError
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, StructType
from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.contextual.struct.expr.literals import CtxExprLitBool, CtxExprLitFloat, CtxExprLitInt, CtxExprLitStr


class CtxExprExponent(CtxExprNode):

    def __init__(self, base: CtxExprNode, exponent: CtxExprNode, **kwargs):
        super().__init__([base, exponent], src_loc=ComLoc(base.loc.line, base.loc.col_start, exponent.loc.line_end, exponent.loc.col_end), **kwargs)
        self.base: CtxExprNode = base
        self.exponent: CtxExprNode = exponent

    def _get_type(self) -> ComType:
        base_type = self.base.get_type()
        exponent_type = self.exponent.get_type()
        if isinstance(base_type, StructType):
            raise ConversionError(f"StructTypes (`{base_type.render()}`) are not valid exponent bases").with_loc(self.base.loc)
        if isinstance(exponent_type, StructType):
            raise ConversionError(f"StructTypes (`{exponent_type.render()}`) are not valid in exponents").with_loc(self.exponent.loc)
        elif isinstance(base_type, ExecType) and isinstance(exponent_type, ExecType):
            raise ConversionError("Cannot raise executable types to the power of executable types").with_loc(self.loc)
        elif isinstance(base_type, ExecType) and isinstance(exponent_type, InertType):
            raise ConversionError("Cannot raise executable types to the power of inert types").with_loc(self.base.loc)
        elif isinstance(base_type, InertType) and isinstance(exponent_type, ExecType):
            raise ConversionError("Cannot raise inert types to the power of executable types").with_loc(self.exponent.loc)
        elif isinstance(base_type, InertType) and isinstance(exponent_type, InertType):
            match (base_type, exponent_type):
                case (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False), InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.INT, (base_type.const and exponent_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.FLOAT, const=True, nullable=False)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot raise `{self.base.get_type().render()}` to the power of `{self.exponent.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {base_type.render()} vs {exponent_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprExponent(self.base.flatten(), self.exponent.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.base, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.base)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.exponent, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.exponent)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.base, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.exponent, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitInt(int(self.base.value) ** int(self.exponent.value), src_loc=self.loc)
        elif isinstance(self.base, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.exponent, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitFloat(round(float(self.base.value) ** float(self.exponent.value), 12), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprDiv(CtxExprNode):

    def __init__(self, numerator: CtxExprNode, denominator: CtxExprNode, **kwargs):
        super().__init__([numerator, denominator], src_loc=ComLoc(numerator.loc.line, numerator.loc.col_start, denominator.loc.line_end, denominator.loc.col_end), **kwargs)
        self.numerator: CtxExprNode = numerator
        self.denominator: CtxExprNode = denominator

    def _get_type(self) -> ComType:
        numerator_type = self.numerator.get_type()
        denom_type = self.denominator.get_type()
        if isinstance(numerator_type, StructType) or isinstance(denom_type, StructType):
            raise ConversionError(f"StructTypes are not valid in Integer Division")
        elif isinstance(numerator_type, ExecType) and isinstance(denom_type, ExecType):
            raise ConversionError("Cannot divide Executable types")
        elif (isinstance(numerator_type, ExecType) and isinstance(denom_type, InertType)) or (isinstance(numerator_type, InertType) and isinstance(denom_type, ExecType)):
            raise ConversionError("Cannot divide inert types and executable types")
        elif isinstance(numerator_type, InertType) and isinstance(denom_type, InertType):
            match (numerator_type, denom_type):
                case (InertType(InertCoreTypes.INT, nullable=False), InertType(InertCoreTypes.INT, nullable=False)):
                    return InertType(InertCoreTypes.INT, (numerator_type.const and denom_type.const))
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot divide `{self.numerator.get_type().render()}` by `{self.denominator.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {numerator_type.render()} vs {denom_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprDiv(self.numerator.flatten(), self.denominator.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.numerator, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.numerator)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.denominator, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.denominator)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.numerator, CtxExprLitInt) and isinstance(self.denominator, CtxExprLitInt):
            return CtxExprLitInt(int(self.numerator.value) // int(self.denominator.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprMod(CtxExprNode):

    def __init__(self, left: CtxExprNode, divisor: CtxExprNode, **kwargs):
        super().__init__([left, divisor], src_loc=ComLoc(left.loc.line, left.loc.col_start, divisor.loc.line_end, divisor.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.divisor: CtxExprNode = divisor

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        divisor_type = self.divisor.get_type()
        if isinstance(left_type, StructType) or isinstance(divisor_type, StructType):
            raise ConversionError(f"StructTypes are not valid in Modulo division")
        elif isinstance(left_type, ExecType) and isinstance(divisor_type, ExecType):
            raise ConversionError("Cannot modulo Executable types")
        elif (isinstance(left_type, ExecType) and isinstance(divisor_type, InertType)) or (isinstance(left_type, InertType) and isinstance(divisor_type, ExecType)):
            raise ConversionError("Cannot modulo inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(divisor_type, InertType):
            match (left_type, divisor_type):
                case (InertType(InertCoreTypes.INT, nullable=False), InertType(InertCoreTypes.INT, nullable=False)):
                    return InertType(InertCoreTypes.INT, (left_type.const and divisor_type.const))
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot modulo `{self.left.get_type().render()}` and `{self.divisor.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {divisor_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprMod(self.left.flatten(), self.divisor.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.divisor, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.divisor)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, CtxExprLitInt) and isinstance(self.divisor, CtxExprLitInt):
            return CtxExprLitInt(int(self.left.value) % int(self.divisor.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprMult(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType) or isinstance(right_type, StructType):
            raise ConversionError(f"StructTypes are not valid in multiplication")
        elif isinstance(left_type, ExecType) and isinstance(right_type, ExecType):
            raise ConversionError("Cannot multiply Executable types")
        elif (isinstance(left_type, ExecType) and isinstance(right_type, InertType)) or (isinstance(left_type, InertType) and isinstance(right_type, ExecType)):
            raise ConversionError("Cannot multiply inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.INT, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.FLOAT, const=True, nullable=False)
                case (InertType(InertCoreTypes.STR, const=True, nullable=False), InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.STR, const=True, nullable=False)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot multiply `{self.left.get_type().render()}` and `{self.right.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprMult(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitInt(int(self.left.value) * int(self.right.value), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitFloat(round(float(self.left.value) * float(self.right.value), 12), src_loc=self.loc)
        elif isinstance(self.left, CtxExprLitStr) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitStr(str(self.left.value) * int(self.right.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprMinus(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType) or isinstance(right_type, StructType):
            raise ConversionError(f"StructTypes are not valid in Subtraction")
        elif isinstance(left_type, ExecType) and isinstance(right_type, ExecType):
            match (left_type, right_type):
                case (ExecType(ExecCoreTypes.PLAYER), ExecType(ExecCoreTypes.PLAYER | ExecCoreTypes.ENTITY)):
                    return ExecType(ExecCoreTypes.PLAYER, left_type.group)
                case (ExecType(ExecCoreTypes.ENTITY), ExecType(ExecCoreTypes.PLAYER | ExecCoreTypes.ENTITY)):
                    return ExecType(ExecCoreTypes.ENTITY, left_type.group)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot subtract from `{self.left.get_type().render()}` the type `{self.right.get_type().render()}`")
        elif (isinstance(left_type, ExecType) and isinstance(right_type, InertType)) or (isinstance(left_type, InertType) and isinstance(right_type, ExecType)):
            raise ConversionError("Cannot subtract inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.INT, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.FLOAT, const=True, nullable=False)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot subtract from `{self.left.get_type().render()}` the type `{self.right.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprMinus(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitInt(int(self.left.value) - int(self.right.value), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitFloat(round(float(self.left.value) - float(self.right.value), 12), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")


class CtxExprPlus(CtxExprNode):

    def __init__(self, left: CtxExprNode, right: CtxExprNode, **kwargs):
        super().__init__([left, right], src_loc=ComLoc(left.loc.line, left.loc.col_start, right.loc.line_end, right.loc.col_end), **kwargs)
        self.left: CtxExprNode = left
        self.right: CtxExprNode = right

    def _get_type(self) -> ComType:
        left_type = self.left.get_type()
        right_type = self.right.get_type()
        if isinstance(left_type, StructType) or isinstance(right_type, StructType):
            raise ConversionError(f"StructTypes are not valid in Addition")
        elif isinstance(left_type, ExecType) and isinstance(right_type, ExecType):
            match (left_type, right_type):
                case (ExecType(ExecCoreTypes.PLAYER), ExecType(ExecCoreTypes.PLAYER)):
                    return ExecType(ExecCoreTypes.PLAYER, True)
                case (ExecType(ExecCoreTypes.PLAYER | ExecCoreTypes.ENTITY), ExecType(ExecCoreTypes.PLAYER | ExecCoreTypes.ENTITY)):
                    return ExecType(ExecCoreTypes.ENTITY, True)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot add `{self.left.get_type().render()}` and `{self.right.get_type().render()}`")
        elif (isinstance(left_type, ExecType) and isinstance(right_type, InertType)) or (isinstance(left_type, InertType) and isinstance(right_type, ExecType)):
            raise ConversionError("Cannot add inert types and executable types")
        elif isinstance(left_type, InertType) and isinstance(right_type, InertType):
            match (left_type, right_type):
                case   (InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False),
                        InertType(InertCoreTypes.INT | InertCoreTypes.BOOL, nullable=False)):
                    return InertType(InertCoreTypes.INT, (left_type.const and right_type.const))
                case   (InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False),
                        InertType(InertCoreTypes.FLOAT | InertCoreTypes.INT | InertCoreTypes.BOOL, const=True, nullable=False)):
                    return InertType(InertCoreTypes.FLOAT, const=True, nullable=False)
                case (InertType(InertCoreTypes.STR, const=True, nullable=False), InertType(InertCoreTypes.STR, const=True, nullable=False)):
                    return InertType(InertCoreTypes.STR, const=True, nullable=False)
                case _:
                    raise ConversionError(f"Invalid operation types: Cannot add `{self.left.get_type().render()}` and `{self.right.get_type().render()}`")
        else:
            raise UnreachableError(f"Type types unexpectedly did not match any option {left_type.render()} vs {right_type.render()}")

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprPlus(self.left.flatten(), self.right.flatten())

    def _flatten_body(self) -> 'CtxExprLits':
        if not isinstance(self.left, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.left)}) of flattened `{type(self).__name__}` encountered")
        if not isinstance(self.right, CtxExprLits):
            raise ContextualisationError(f"Non-literal child ({type(self.right)}) of flattened `{type(self).__name__}` encountered")

        if isinstance(self.left, (CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitInt(int(self.left.value) + int(self.right.value), src_loc=self.loc)
        elif isinstance(self.left, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)) and isinstance(self.right, (CtxExprLitFloat, CtxExprLitInt, CtxExprLitBool)):
            return CtxExprLitFloat(round(float(self.left.value) + float(self.right.value), 12), src_loc=self.loc)
        elif isinstance(self.left, CtxExprLitStr) and isinstance(self.right, CtxExprLitStr):
            return CtxExprLitStr(str(self.left.value) + str(self.right.value), src_loc=self.loc)
        else:
            my_type = self.get_type()
            raise ContextualisationError(f"Cannot flatten `{type(self).__name__}` node of type `{my_type}`")
