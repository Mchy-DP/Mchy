
from typing import Optional
import pytest
from mchy.common.com_loc import ComLoc
from mchy.contextual.struct.stmnt import MarkerDeclVar
from mchy.contextual.struct.var_scope import CtxVar
from mchy.errors import ConversionError
from mchy.contextual.struct import ComType, CtxExprNode
from mchy.common.com_types import ExecCoreTypes, ExecType, InertType
from mchy.contextual.struct.expr import *
from tests.common_tests.helpers import BOOL, INT, FLOAT, STR, WORLD, ENTITY, PLAYER
from tests.contextual_layer.helpers import CtxTTypeNode

_LOC = ComLoc()


@pytest.mark.parametrize("expr, expected_type", [
    # Lits
    (CtxExprLitInt(42, src_loc=_LOC), InertType(INT, True, False)),
    (CtxExprLitFloat(3.14, src_loc=_LOC), InertType(FLOAT, True, False)),
    (CtxExprLitStr("foo", src_loc=_LOC), InertType(STR, True, False)),
    # Plus
    (CtxExprPlus(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprPlus(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(INT, True, False)),
    (CtxExprPlus(CtxTTypeNode(InertType(INT, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprPlus(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprPlus(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprPlus(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(INT, False, False)),
    (CtxExprPlus(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprPlus(CtxTTypeNode(InertType(BOOL, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprPlus(CtxExprLitFloat(3.14, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), InertType(FLOAT, True, False)),
    (CtxExprPlus(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitStr("bar", src_loc=_LOC)), InertType(STR, True, False)),
    (CtxExprPlus(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), None),
    # Plus-exec
    (CtxExprPlus(CtxTTypeNode(ExecType(ENTITY, True)), CtxTTypeNode(ExecType(ENTITY, True))), ExecType(ENTITY, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(ENTITY, True))), ExecType(ENTITY, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(ENTITY, True)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(ENTITY, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(PLAYER, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(PLAYER, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(PLAYER, False))), ExecType(PLAYER, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(PLAYER, False))), ExecType(PLAYER, True)),
    (CtxExprPlus(CtxTTypeNode(ExecType(WORLD, False)), CtxTTypeNode(ExecType(PLAYER, False))), None),
    (CtxExprPlus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(WORLD, False))), None),
    (CtxExprPlus(CtxTTypeNode(ExecType(WORLD, False)), CtxTTypeNode(ExecType(WORLD, False))), None),
    # Minus
    (CtxExprMinus(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprMinus(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(INT, True, False)),
    (CtxExprMinus(CtxTTypeNode(InertType(INT, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprMinus(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprMinus(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprMinus(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(INT, False, False)),
    (CtxExprMinus(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprMinus(CtxTTypeNode(InertType(BOOL, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprMinus(CtxExprLitFloat(3.14, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), InertType(FLOAT, True, False)),
    (CtxExprMinus(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitStr("bar", src_loc=_LOC)), None),
    (CtxExprMinus(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), None),
    # minus-exec
    (CtxExprMinus(CtxTTypeNode(ExecType(ENTITY, True)), CtxTTypeNode(ExecType(ENTITY, True))), ExecType(ENTITY, True)),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(ENTITY, True))), ExecType(PLAYER, True)),
    (CtxExprMinus(CtxTTypeNode(ExecType(ENTITY, True)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(ENTITY, True)),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(PLAYER, True)),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(PLAYER, True))), ExecType(PLAYER, False)),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(PLAYER, False))), ExecType(PLAYER, False)),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, True)), CtxTTypeNode(ExecType(PLAYER, False))), ExecType(PLAYER, True)),
    (CtxExprMinus(CtxTTypeNode(ExecType(WORLD, False)), CtxTTypeNode(ExecType(PLAYER, False))), None),
    (CtxExprMinus(CtxTTypeNode(ExecType(PLAYER, False)), CtxTTypeNode(ExecType(WORLD, False))), None),
    (CtxExprMinus(CtxTTypeNode(ExecType(WORLD, False)), CtxTTypeNode(ExecType(WORLD, False))), None),
    # Mult
    (CtxExprMult(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprMult(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(INT, True, False)),
    (CtxExprMult(CtxTTypeNode(InertType(INT, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprMult(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprMult(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprMult(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(INT, False, False)),
    (CtxExprMult(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprMult(CtxTTypeNode(InertType(BOOL, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprMult(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitStr("bar", src_loc=_LOC)), None),
    (CtxExprMult(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), InertType(STR, True, False)),
    (CtxExprMult(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitFloat(3.14, src_loc=_LOC)), None),
    (CtxExprMult(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitStr("foo", src_loc=_LOC)), None),
    # Div
    (CtxExprDiv(CtxExprLitInt(12, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprDiv(CtxExprLitInt(12, src_loc=_LOC), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprDiv(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprDiv(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    # Mod
    (CtxExprMod(CtxExprLitInt(12, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprMod(CtxExprLitInt(12, src_loc=_LOC), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprMod(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprMod(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    # Exponent
    (CtxExprExponent(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(INT, True, False)),
    (CtxExprExponent(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(INT, True, False)),
    (CtxExprExponent(CtxTTypeNode(InertType(INT, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprExponent(CtxTTypeNode(InertType(INT, True, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprExponent(CtxTTypeNode(InertType(INT, False, True)), CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprExponent(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(INT, False, False)),
    (CtxExprExponent(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprExponent(CtxTTypeNode(InertType(BOOL, False, False)), CtxExprLitInt(3, src_loc=_LOC)), InertType(INT, False, False)),
    (CtxExprExponent(CtxExprLitFloat(3.14, src_loc=_LOC), CtxExprLitInt(2, src_loc=_LOC)), InertType(FLOAT, True, False)),
    (CtxExprExponent(CtxExprLitInt(2, src_loc=_LOC), CtxExprLitFloat(3.14, src_loc=_LOC)), InertType(FLOAT, True, False)),
    (CtxExprExponent(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitStr("bar", src_loc=_LOC)), None),
    (CtxExprExponent(CtxExprLitStr("foo", src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)), None),
    # Comparison : EQUALITY
    (CtxExprCompEquality(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(4, src_loc=_LOC)), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(BOOL, False, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, True, False)), CtxTTypeNode(InertType(STR, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, True, False)), CtxTTypeNode(InertType(STR, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, False, False)), CtxTTypeNode(InertType(STR, True, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, False, False)), CtxTTypeNode(InertType(STR, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, False, False)), CtxTTypeNode(InertType(INT, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, False, False)), CtxTTypeNode(InertType(INT, True, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(STR, True, False)), CtxTTypeNode(InertType(INT, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, True, False)), CtxTTypeNode(InertType(FLOAT, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, True, False)), CtxTTypeNode(InertType(INT, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, True, False)), CtxTTypeNode(InertType(STR, True, False))), InertType(BOOL, True, False)),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, False, False)), CtxTTypeNode(InertType(FLOAT, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, True, False)), CtxTTypeNode(InertType(FLOAT, False, False))), None),
    (CtxExprCompEquality(CtxTTypeNode(InertType(FLOAT, False, False)), CtxTTypeNode(InertType(FLOAT, True, False))), None),
    # Boolean Operators
    (CtxExprNot(CtxExprLitBool(True, src_loc=_LOC)), InertType(BOOL, True, False)),
    (CtxExprNot(CtxExprLitInt(3, src_loc=_LOC)), None),
    (CtxExprAnd(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)), InertType(BOOL, True, False)),
    (CtxExprAnd(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, True, False)),
    (CtxExprAnd(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, False, False)),
    (CtxExprAnd(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprAnd(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprAnd(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), None),
    (CtxExprAnd(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), None),
    (CtxExprOr(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)), InertType(BOOL, True, False)),
    (CtxExprOr(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, True, False)),
    (CtxExprOr(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, False, False)),
    (CtxExprOr(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprOr(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprOr(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), None),
    (CtxExprOr(CtxTTypeNode(InertType(INT, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), None),
    # Null Coalescing
    (CtxExprNullCoal(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(False, src_loc=_LOC)), InertType(BOOL, True, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, True, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(BOOL, True, False))), InertType(BOOL, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(BOOL, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, True, False)), CtxTTypeNode(InertType(STR, True, False))), None),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(FLOAT, False, False))), InertType(FLOAT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(FLOAT, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(FLOAT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(BOOL, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(BOOL, False, False))), InertType(INT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(INT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(FLOAT, False, False)), CtxTTypeNode(InertType(INT, False, False))), InertType(FLOAT, False, False)),
    (CtxExprNullCoal(CtxTTypeNode(InertType(INT, False, False)), CtxTTypeNode(InertType(FLOAT, False, False))), InertType(FLOAT, False, False)),
])
def test_expr_type_correct(expr: CtxExprNode, expected_type: Optional[ComType]):
    if expected_type is None:
        with pytest.raises(ConversionError):
            expr.get_type()
    else:
        assert expr.get_type() == expected_type


def test_expr_plus_errors_when_inert_and_expr():
    expr = CtxExprPlus(CtxExprVar(CtxVar("foo", ExecType(ExecCoreTypes.PLAYER, False), False, MarkerDeclVar()), src_loc=ComLoc()), CtxExprLitInt(42, src_loc=ComLoc()))
    with pytest.raises(ConversionError) as err_info:
        expr.get_type()
    assert "operation types" not in str(err_info.value)
