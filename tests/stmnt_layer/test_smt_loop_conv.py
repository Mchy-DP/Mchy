
from typing import List
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual import struct as ctxs
from mchy.contextual.struct.module import CtxModule
from mchy.contextual.struct.stmnt import CtxBranch, CtxIfStmnt, CtxWhileLoop, MarkerDeclVar
from mchy.stmnt.generation import convert
from mchy.stmnt.struct import cmds as smt_cmds
from mchy.stmnt.struct.atoms import SmtConstInt, SmtPublicVar, SmtWorld
from mchy.stmnt.struct.smt_frag import RoutingFlavour, SmtFragment
from tests.stmnt_layer.helper import diff_cmds_list


_INT = InertType(InertCoreTypes.INT)


def test_simple_smt_while_conv():
    module = CtxModule(Config())
    _int_var_foo = module.global_var_scope.register_new_var("foo", _INT, False, MarkerDeclVar().with_enclosing_function(None))
    module.exec_body.append(CtxWhileLoop(ctxs.CtxExprLitBool(True, src_loc=ComLoc()), [ctxs.CtxAssignment(_int_var_foo, ctxs.CtxExprLitInt(11, src_loc=ComLoc()))]))

    smt_module = convert(module, config=Config())

    # check correct fragments exist
    frags: List[SmtFragment] = [smt_module.initial_function.func_frag] + smt_module.initial_function.fragments
    assert len(frags) == 4  # func_frag, cond, body, exit
    assert len(frags[0].route) == 0, f"First fragment not func_frag ({frags[0]})"
    assert len(frags[1].route) == 1 and frags[1].route[0].flavour == RoutingFlavour.COND, f"Second fragment not passover ({frags[1]})"
    assert len(frags[2].route) == 1 and frags[2].route[0].flavour == RoutingFlavour.LOOP, f"Third fragment not if-taken ({frags[2]})"
    assert len(frags[3].route) == 1 and frags[3].route[0].flavour == RoutingFlavour.TOP, f"Third fragment not if-taken ({frags[2]})"

    func_frag = frags[0]
    cond = frags[1]
    loop_body = frags[2]
    loop_exit = frags[3]

    # check fragment bodies are as expected
    diff_bool, explanation = diff_cmds_list(func_frag.body, [
        smt_cmds.SmtConditionalInvokeFuncCmd([(SmtConstInt(1), True)], smt_module.initial_function, cond, SmtWorld()),
    ])
    assert diff_bool, "generated command list does not match expected:\n" + explanation

    diff_bool, explanation = diff_cmds_list(cond.body, [
        smt_cmds.SmtConditionalInvokeFuncCmd([(SmtConstInt(1), False)], smt_module.initial_function, loop_exit, SmtWorld()),
        smt_cmds.SmtConditionalInvokeFuncCmd([(SmtConstInt(1), True)], smt_module.initial_function, loop_body, SmtWorld()),
    ])
    assert diff_bool, "generated command list does not match expected:\n" + explanation

    diff_bool, explanation = diff_cmds_list(loop_body.body, [
        smt_cmds.SmtAssignCmd(SmtPublicVar("foo", _INT), SmtConstInt(11)),
        smt_cmds.SmtConditionalInvokeFuncCmd([(SmtConstInt(1), True)], smt_module.initial_function, cond, SmtWorld()),
    ])
    assert diff_bool, "generated command list does not match expected:\n" + explanation

    diff_bool, explanation = diff_cmds_list(loop_exit.body, [])
    assert diff_bool, "generated command list does not match expected:\n" + explanation
