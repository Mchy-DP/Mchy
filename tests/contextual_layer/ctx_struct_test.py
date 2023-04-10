
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_types import ExecCoreTypes, ExecType
from mchy.common.config import Config
from mchy.contextual.generation import convert
from mchy.mchy_ast.nodes import *
from mchy.contextual.struct import CtxModule
from mchy.contextual.struct.expr import *
from mchy.contextual.expr_generation import convert_expr

import pytest


def test_flatten_struct():
    module = CtxModule(Config())
    module.import_ns(Namespace.get_namespace("std"))
    pos_struct = module.get_struct("Pos")
    if pos_struct is None:
        raise ValueError("Failed to import std library in testing")
    ast_expr = ExprFuncCall(
        ExprPropertyAccess(
            ExprLitWorld(None),
            ExprLitIdent("pos")
        ),
        ExprLitIdent("constant"),
        ExprFragParam(label=ExprLitIdent("x"), value=ExprLitInt(5)),
        ExprFragParam(label=ExprLitIdent("y"), value=ExprLitInt(7)),
        ExprFragParam(label=ExprLitIdent("z"), value=ExprLitInt(9))
    )
    expected_ctx_expr = CtxExprPyStruct(pos_struct, {"x": 5.0, "y": 7.0, "z": 9.0})
    observed_ctx_expr = convert_expr(ast_expr, ExecType(ExecCoreTypes.WORLD, False), module, [module.global_var_scope])
    assert observed_ctx_expr == expected_ctx_expr


def test_flatten_struct_var():
    # Setup
    config = Config()
    ast = Root(Scope(Stmnt(VariableDecl(
        False, TypeNode("Pos"), ExprLitIdent("foo"),
        ExprFuncCall(
            ExprPropertyAccess(
                ExprLitWorld(None),
                ExprLitIdent("pos")
            ),
            ExprLitIdent("constant"),
            ExprFragParam(label=ExprLitIdent("x"), value=ExprLitInt(5)),
            ExprFragParam(label=ExprLitIdent("y"), value=ExprLitInt(7)),
            ExprFragParam(label=ExprLitIdent("z"), value=ExprLitInt(9))
        )
    ))))
    module = convert(ast, config)
    pos_struct = module.get_struct("Pos")
    if pos_struct is None:
        raise ValueError("Failed to import std library in testing")
    # test variable flattening
    expected_ctx_expr = CtxExprPyStruct(pos_struct, {"x": 5.0, "y": 7.0, "z": 9.0})
    observed_ctx_expr = convert_expr(ExprLitIdent("foo"), None, module, [module.global_var_scope])
    assert observed_ctx_expr == expected_ctx_expr
