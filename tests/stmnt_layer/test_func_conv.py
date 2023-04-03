
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.struct import *
from mchy.contextual.struct.expr import CtxExprLitWorld
from mchy.stmnt.struct import *
from mchy.stmnt.generation import convert
from tests.stmnt_layer.helper import diff_cmds_list

import pytest

from mchy.stmnt.struct.cmds import SmtInvokeFuncCmd

_INT = InertType(InertCoreTypes.INT)


class TestMchyFunc1:

    _MODULE = CtxModule(Config())
    _MARKER_GET42 = MarkerDeclFunc([])
    _FUNC_GET42 = CtxMchyFunc(ExecType(ExecCoreTypes.WORLD, False), ComLoc(), "get42", [], InertType(InertCoreTypes.INT), ComLoc(), _MARKER_GET42)
    _MARKER_GET42.with_func(_FUNC_GET42)
    _MODULE.add_function(_FUNC_GET42)
    _INT_VAR_FOO = _MODULE.global_var_scope.register_new_var("foo", InertType(InertCoreTypes.INT), False, MarkerDeclVar().with_enclosing_function(None))

    _FUNC_GET42.exec_body = [
        CtxReturn(CtxExprLitInt(42, src_loc=ComLoc()))
    ]

    _MODULE.exec_body = [
        _MARKER_GET42,
        CtxAssignment(_INT_VAR_FOO, CtxExprFuncCall(CtxExprLitWorld(src_loc=ComLoc()), _FUNC_GET42, [], src_loc=ComLoc())),
    ]

    @pytest.fixture
    def ctx_module(self) -> CtxModule:
        TestMchyFunc1._FUNC_GET42.exec_body = [
            CtxReturn(CtxExprLitInt(42, src_loc=ComLoc()))
        ]

        TestMchyFunc1._MODULE.exec_body = [
            TestMchyFunc1._MARKER_GET42,
        ]
        return TestMchyFunc1._MODULE

    def test_converted_function_exists(self, ctx_module: CtxModule):
        smt_module = convert(ctx_module, Config())
        assert TestMchyFunc1._FUNC_GET42 in smt_module._mchy_funcs_link.keys()

    def test_calling_mchy_function_works(self, ctx_module: CtxModule):
        ctx_module.exec_body.append(
            CtxAssignment(TestMchyFunc1._INT_VAR_FOO, CtxExprFuncCall(CtxExprLitWorld(src_loc=ComLoc()), TestMchyFunc1._FUNC_GET42, [], src_loc=ComLoc()))
        )
        smt_module = convert(ctx_module, Config())

        func = smt_module.get_smt_func(TestMchyFunc1._FUNC_GET42)
        diff_bool, explanation = diff_cmds_list(smt_module.initial_function.func_frag.body, [
            SmtInvokeFuncCmd(func, SmtWorld()),
            SmtSpecialStackIncSourceAssignCmd(SmtPseudoVar(0, func.return_var.get_type()), func.return_var),
            SmtAssignCmd(SmtPublicVar('foo', _INT), SmtPseudoVar(0, func.return_var.get_type())),
        ])
        assert diff_bool, "Converted function call does not match expected:\n" + explanation

    def test_converted_function_has_correct_body(self, ctx_module: CtxModule):
        smt_module = convert(ctx_module, Config())
        func = smt_module.get_smt_func(TestMchyFunc1._FUNC_GET42)
        assert len(func.func_frag.body) > 0, "Empty function body?"

        diff_bool, explanation = diff_cmds_list(func.func_frag.body, [SmtAssignCmd(func.return_var, SmtConstInt(42))])
        assert diff_bool, "Converted function body does not match expected:\n" + explanation
