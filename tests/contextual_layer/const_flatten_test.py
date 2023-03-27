
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_types import ExecCoreTypes, ExecType
from mchy.common.config import Config
from mchy.mchy_ast.nodes import *
from mchy.contextual.struct import CtxModule
from mchy.contextual.struct.expr import *
from mchy.contextual.expr_generation import convert_expr

import pytest

MODULE = CtxModule(Config())
_LOC = ComLoc()


# Helps test flatten works as expected
@pytest.mark.parametrize("ast_expr, expected_ctx_expr", [
    # Literals
    (ExprLitNull(None), CtxExprLitNull(src_loc=_LOC)),
    (ExprLitWorld(None), CtxExprLitWorld(src_loc=_LOC)),
    (ExprLitBool(False), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprLitBool(True), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprLitInt(42), CtxExprLitInt(42, src_loc=_LOC)),
    (ExprLitFloat(3.14), CtxExprLitFloat(3.14, src_loc=_LOC)),

    # Math
    (ExprPlus(ExprLitInt(5), ExprLitInt(7)), CtxExprLitInt(12, src_loc=_LOC)),
    (ExprPlus(ExprLitFloat(2.5), ExprLitFloat(3.5)), CtxExprLitFloat(6.0, src_loc=_LOC)),
    (ExprPlus(ExprLitStr("foo"), ExprLitStr("bar")), CtxExprLitStr("foobar", src_loc=_LOC)),
    (ExprMinus(ExprLitInt(9), ExprLitInt(3)), CtxExprLitInt(6, src_loc=_LOC)),
    (ExprMinus(ExprLitFloat(4.5), ExprLitFloat(1.3)), CtxExprLitFloat(3.2, src_loc=_LOC)),
    (ExprMult(ExprLitInt(3), ExprLitInt(9)), CtxExprLitInt(27, src_loc=_LOC)),
    (ExprMult(ExprLitFloat(2.5), ExprLitInt(5)), CtxExprLitFloat(12.5, src_loc=_LOC)),
    (ExprMult(ExprLitFloat(2.5), ExprLitFloat(5.0)), CtxExprLitFloat(12.5, src_loc=_LOC)),
    (ExprMult(ExprLitStr("abc-"), ExprLitInt(2)), CtxExprLitStr("abc-abc-", src_loc=_LOC)),
    (ExprDiv(ExprLitInt(19), ExprLitInt(7)), CtxExprLitInt(2, src_loc=_LOC)),
    (ExprMod(ExprLitInt(19), ExprLitInt(7)), CtxExprLitInt(5, src_loc=_LOC)),
    (ExprExponent(ExprLitInt(5), ExprLitInt(3)), CtxExprLitInt(125, src_loc=_LOC)),
    (ExprExponent(ExprLitFloat(1.5), ExprLitInt(2)), CtxExprLitFloat(2.25, src_loc=_LOC)),

    # Comparison - EQUALITY
    (ExprEquality(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(1), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(0), ExprLitBool(True)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(0), ExprLitBool(False)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(2), ExprLitBool(True)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitFloat(1.5), ExprLitFloat(1.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprEquality(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitStr("abc"), ExprLitStr("abc")), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprEquality(ExprLitStr("abc"), ExprLitStr("axc")), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitInt(1), ExprLitStr("axc")), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprEquality(ExprLitBool(True), ExprLitStr("axc")), CtxExprLitBool(False, src_loc=_LOC)),
    # Comparison - INEQUALITY
    (ExprInequality(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(1), ExprLitBool(True)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(0), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(0), ExprLitBool(False)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(2), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitFloat(1.5), ExprLitFloat(1.5)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprInequality(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitStr("abc"), ExprLitStr("abc")), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprInequality(ExprLitStr("abc"), ExprLitStr("axc")), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitInt(1), ExprLitStr("axc")), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprInequality(ExprLitBool(True), ExprLitStr("axc")), CtxExprLitBool(True, src_loc=_LOC)),
    # Comparison -  `>=` `=` `<=` `<`
    # --- int test
    (ExprCompGTE(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGTE(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGTE(ExprLitInt(81), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGT(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGT(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGT(ExprLitInt(81), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLTE(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLTE(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLTE(ExprLitInt(81), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompLT(ExprLitInt(13), ExprLitInt(42)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLT(ExprLitInt(42), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompLT(ExprLitInt(81), ExprLitInt(42)), CtxExprLitBool(False, src_loc=_LOC)),
    # --- float handling
    (ExprCompGTE(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGTE(ExprLitFloat(2.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGTE(ExprLitFloat(3.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGTE(ExprLitFloat(1.5), ExprLitInt(2)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGTE(ExprLitFloat(2.0), ExprLitInt(2)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGTE(ExprLitFloat(2.5), ExprLitInt(2)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompGT(ExprLitFloat(2.5), ExprLitFloat(2.5)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompGT(ExprLitFloat(2.0), ExprLitInt(2)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprCompLTE(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLT(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLTE(ExprLitFloat(2.5), ExprLitFloat(2.5)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprCompLT(ExprLitFloat(2.5), ExprLitFloat(2.5)), CtxExprLitBool(False, src_loc=_LOC)),
    # Boolean operators:
    (ExprNot(ExprLitBool(True)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprNot(ExprLitBool(False)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprAnd(ExprLitBool(True), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprAnd(ExprLitBool(False), ExprLitBool(True)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprAnd(ExprLitBool(True), ExprLitBool(False)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprAnd(ExprLitBool(False), ExprLitBool(False)), CtxExprLitBool(False, src_loc=_LOC)),
    (ExprOr(ExprLitBool(True), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprOr(ExprLitBool(False), ExprLitBool(True)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprOr(ExprLitBool(True), ExprLitBool(False)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprOr(ExprLitBool(False), ExprLitBool(False)), CtxExprLitBool(False, src_loc=_LOC)),
    # Null Coalescing
    (ExprNullCoal(ExprLitBool(True), ExprLitBool(False)), CtxExprLitBool(True, src_loc=_LOC)),
    (ExprNullCoal(ExprLitFloat(1.5), ExprLitFloat(2.5)), CtxExprLitFloat(1.5, src_loc=_LOC)),
    (ExprNullCoal(ExprLitNull(None), ExprLitFloat(2.5)), CtxExprLitFloat(2.5, src_loc=_LOC)),
])
def test_convert_expr(ast_expr: ExprGen, expected_ctx_expr: CtxExprNode):
    assert (
        convert_expr(ast_expr, ExecType(ExecCoreTypes.WORLD, False), MODULE, [MODULE.global_var_scope]) == expected_ctx_expr
    ), f"Expression did not flatten as expected: \n" + str(ast_expr.__dict__)
