
from typing import Dict, List, Optional, Type
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.abs_ctx import AbsCtxParam
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.struct import *
from mchy.contextual.struct.expr.chains import CtxChain, CtxChainLink
from mchy.library.std.chain_entity_selector import ChainLinkGetEntities, ChainLinkPartialEntitiesSelectorWithTag, ChainPartialEntitiesSelectorFind
from mchy.stmnt.struct import *
from mchy.stmnt.generation import convert
from mchy.stmnt.struct.cmds.tag_ops import SmtRawEntitySelector
from tests.stmnt_layer.helper import diff_cmds_list

import pytest

_INT = InertType(InertCoreTypes.INT)

_MODULE = CtxModule(Config())
_MODULE.import_ns(Namespace.get_namespace("std"))
_INT_VAR = _MODULE.global_var_scope.register_new_var("foo", InertType(InertCoreTypes.INT), False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_INT_VAR2 = _MODULE.global_var_scope.register_new_var("bar", InertType(InertCoreTypes.INT), False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_BOOL_VAR = _MODULE.global_var_scope.register_new_var("fooboo", InertType(InertCoreTypes.BOOL), False, MarkerDeclVar().with_enclosing_function(None), ComLoc())
_GENT_VAR = _MODULE.global_var_scope.register_new_var("ents", ExecType(ExecCoreTypes.ENTITY, True), False, MarkerDeclVar().with_enclosing_function(None), ComLoc())


def _ctx_chainlink_helper(ichainlink_type: Type[IChainLink], data: Dict[str, CtxExprNode]) -> CtxChainLink:
    ichainlink = [link for link in _MODULE._chain_links if isinstance(link, ichainlink_type)][0]
    link = CtxChainLink(ichainlink)
    arg_binding: Dict[AbsCtxParam, Optional['CtxExprNode']] = {}
    for ctx_param in ichainlink.get_ctx_params():
        arg_binding[ctx_param] = data.get(ctx_param.get_label(), None)
    link.set_chain_data(arg_binding)
    return link


def _ctx_chain_helper(ichain_type: Type[IChain], data: Dict[str, CtxExprNode]) -> CtxChain:
    ichain = [link for link in _MODULE._chain_links if isinstance(link, ichain_type)][0]
    link = CtxChain(ichain, _MODULE)
    arg_binding: Dict[AbsCtxParam, Optional['CtxExprNode']] = {}
    for ctx_param in ichain.get_ctx_params():
        arg_binding[ctx_param] = data.get(ctx_param.get_label(), None)
    link.set_chain_data(arg_binding)
    return link


def test_ctx_2_smt_selector_chain_double_clink():
    stmnts: List[CtxStmnt] = [
        CtxAssignment(_GENT_VAR, CtxExprFinalChain(CtxExprLitWorld(src_loc=ComLoc()), [
            _ctx_chainlink_helper(ChainLinkGetEntities, {}),
            _ctx_chainlink_helper(ChainLinkPartialEntitiesSelectorWithTag, {"tag": CtxExprLitStr("foo", src_loc=ComLoc())}),
            _ctx_chainlink_helper(ChainLinkPartialEntitiesSelectorWithTag, {"tag": CtxExprLitStr("bar", src_loc=ComLoc())}),
        ], _ctx_chain_helper(ChainPartialEntitiesSelectorFind, {}), src_loc=ComLoc()
        ))
    ]
    expected_cmd_list: List[SmtCmd] = [
        SmtRawEntitySelector(SmtWorld(), SmtPseudoVar(0, _INT), "@e[tag=foo,tag=bar]"),
        SmtAssignCmd(SmtPublicVar("ents", _INT), SmtPseudoVar(0, _INT))
    ]

    _MODULE.exec_body = stmnts
    smt_module = convert(_MODULE, Config())

    diff_bool, explanation = diff_cmds_list(smt_module.initial_function.func_frag.body, expected_cmd_list)
    assert diff_bool, "generated command list does not match expected:\n" + explanation
