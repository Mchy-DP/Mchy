
from typing import List
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.struct import *
from mchy.stmnt.struct import *
from mchy.stmnt.generation import convert
from tests.stmnt_layer.helper import diff_cmds_list

import pytest

_INT = InertType(InertCoreTypes.INT)
_NULLABLE_INT = InertType(InertCoreTypes.INT, nullable=True)

_MODULE = CtxModule(Config())
_INT_VAR = _MODULE.global_var_scope.register_new_var("foo", _INT, False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_INT_VAR2 = _MODULE.global_var_scope.register_new_var("bar", _INT, False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_NULLABLE_INT_VAR = _MODULE.global_var_scope.register_new_var("nullish", _NULLABLE_INT, False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_BOOL_VAR = _MODULE.global_var_scope.register_new_var("fooboo", InertType(InertCoreTypes.BOOL), False, MarkerDeclVar().with_enclosing_function(None), ComLoc())

_LOC = ComLoc()


@pytest.mark.parametrize("stmnts, expected_cmd_list", [
    ([CtxAssignment(_INT_VAR, CtxExprLitInt(42, src_loc=_LOC))], [SmtAssignCmd(SmtPublicVar("foo", _INT), SmtConstInt(42))]),
    ([CtxAssignment(_INT_VAR, CtxExprLitBool(True, src_loc=_LOC))], [SmtAssignCmd(SmtPublicVar("foo", _INT), SmtConstInt(1))]),
    ([CtxAssignment(_INT_VAR, CtxExprPlus(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitInt(7, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(3)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtConstInt(7)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprMinus(CtxExprLitInt(9, src_loc=_LOC), CtxExprLitInt(2, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(9)),
        SmtMinusCmd(SmtPseudoVar(0, _INT), SmtConstInt(2)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprMult(CtxExprLitInt(9, src_loc=_LOC), CtxExprLitInt(2, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(9)),
        SmtMultCmd(SmtPseudoVar(0, _INT), SmtConstInt(2)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprDiv(CtxExprLitInt(19, src_loc=_LOC), CtxExprLitInt(7, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(19)),
        SmtDivCmd(SmtPseudoVar(0, _INT), SmtConstInt(7)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprMod(CtxExprLitInt(19, src_loc=_LOC), CtxExprLitInt(7, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(19)),
        SmtModCmd(SmtPseudoVar(0, _INT), SmtConstInt(7)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprPlus(CtxExprLitInt(10, src_loc=_LOC), CtxExprPlus(CtxExprLitInt(5, src_loc=_LOC), CtxExprLitInt(6, src_loc=_LOC))))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(10)),
        SmtAssignCmd(SmtPseudoVar(1, _INT), SmtConstInt(5)),
        SmtPlusCmd(SmtPseudoVar(1, _INT), SmtConstInt(6)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtPseudoVar(1, _INT)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxExprHolder(CtxExprPlus(CtxExprLitInt(4, src_loc=_LOC), CtxExprLitInt(5, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(4)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtConstInt(5))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprExponent(CtxExprLitInt(5, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(1)),
        SmtMultCmd(SmtPseudoVar(0, _INT), SmtConstInt(5)),
        SmtMultCmd(SmtPseudoVar(0, _INT), SmtConstInt(5)),
        SmtMultCmd(SmtPseudoVar(0, _INT), SmtConstInt(5)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprPlus(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(3)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtConstInt(1)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprPlus(CtxExprLitInt(3, src_loc=_LOC), CtxExprLitBool(False, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(3)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtConstInt(0)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprPlus(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)))], [
        SmtAssignCmd(SmtPseudoVar(0, _INT), SmtConstInt(1)),
        SmtPlusCmd(SmtPseudoVar(0, _INT), SmtConstInt(1)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR2, CtxExprCompEquality(CtxExprVar(_INT_VAR, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtCompEqualityCmd(
            SmtPublicVar("foo", _INT), SmtConstInt(3), SmtPseudoVar(0, _INT),
            SmtPseudoVar(1, _INT), SmtPseudoVar(2, _INT), SmtPseudoVar(3, _INT), SmtPseudoVar(4, _INT)
        ),
        SmtAssignCmd(SmtPublicVar("bar", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR2, CtxExprCompGTE(CtxExprVar(_INT_VAR, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtCompGTECmd(SmtPublicVar("foo", _INT), SmtConstInt(3), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("bar", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR2, CtxExprCompGT(CtxExprVar(_INT_VAR, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtCompGTCmd(SmtPublicVar("foo", _INT), SmtConstInt(3), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("bar", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR2, CtxExprCompLTE(CtxExprVar(_INT_VAR, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtCompGTECmd(SmtConstInt(3), SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("bar", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR2, CtxExprCompLT(CtxExprVar(_INT_VAR, src_loc=_LOC), CtxExprLitInt(3, src_loc=_LOC)))], [
        SmtCompGTCmd(SmtConstInt(3), SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("bar", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprNot(CtxExprLitBool(True, src_loc=_LOC)))], [
        SmtNotCmd(SmtConstInt(1), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprAnd(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)))], [
        SmtAndCmd(SmtConstInt(1), SmtConstInt(1), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprOr(CtxExprLitBool(True, src_loc=_LOC), CtxExprLitBool(True, src_loc=_LOC)))], [
        SmtOrCmd(SmtConstInt(1), SmtConstInt(1), SmtPseudoVar(0, _INT)),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
    ([CtxAssignment(_INT_VAR, CtxExprNullCoal(CtxExprVar(_NULLABLE_INT_VAR, src_loc=_LOC), CtxExprLitInt(10, src_loc=_LOC)))], [
        SmtNullCoalCmd(
            # Useful data
            SmtPublicVar("nullish", _NULLABLE_INT), SmtConstInt(10), SmtPseudoVar(0, _INT),
            # Clobber registers & constant
            SmtPseudoVar(1, _INT), SmtPseudoVar(2, _INT), SmtPseudoVar(3, _INT), SmtPseudoVar(4, _INT), SmtPseudoVar(5, _INT), SmtConstNull()),
        SmtAssignCmd(SmtPublicVar("foo", _INT), SmtPseudoVar(0, _INT))
    ]),
])
def test_stmnt_to_cmd_list(stmnts: List[CtxStmnt], expected_cmd_list: List[SmtCmd]):
    _MODULE.exec_body = stmnts
    smt_module = convert(_MODULE, Config())

    diff_bool, explanation = diff_cmds_list(smt_module.initial_function.func_frag.body, expected_cmd_list)
    assert diff_bool, "generated command list does not match expected:\n" + explanation
