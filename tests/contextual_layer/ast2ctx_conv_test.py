
from mchy.common.com_types import ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.ctx_func import CtxMchyFunc
from mchy.contextual.struct.expr import CtxExprFuncCall, CtxExprLitBool, CtxExprLitInt, CtxExprPlus, CtxExprVar
from mchy.contextual.struct.module import CtxModule
from mchy.contextual.struct.stmnt import CtxExprHolder, CtxIfStmnt, CtxReturn, CtxWhileLoop, MarkerDeclVar
from mchy.contextual.struct.var_scope import CtxVar
from mchy.errors import ConversionError
from mchy.mchy_ast.nodes import *
from mchy.contextual.generation import convert

import pytest


def test_e2h_convert_empty_root():
    ast_root = Root(Scope())
    module = convert(ast_root, Config())

    assert module.get_function(ExecType(ExecCoreTypes.WORLD, False), "say") is not None,  "std library is not loaded on converted ast's"


def test_e2h_convert_if_stmnt():
    ast_root = Root(Scope(Stmnt(IfStruct(
            ExprLitBool(False),
            CodeBlock(Stmnt(ExprLitInt(11))),
            ElifStruct(ExprLitBool(True), CodeBlock(Stmnt(ExprLitInt(22)))),
            ElseStruct(CodeBlock(Stmnt(ExprLitInt(33))))
        ))))

    module = convert(ast_root, Config())

    assert len(module.exec_body) == 1, f"Module does not have exactly one body statement ({str(module.exec_body)})"
    if_stmnt = module.exec_body[0]
    assert isinstance(if_stmnt, CtxIfStmnt), f"Module statement is not a CtxIfStmnt, found: ({str(if_stmnt)})"

    assert if_stmnt.if_branch.cond == CtxExprLitBool(False, src_loc=ComLoc())
    assert isinstance(if_stmnt.if_branch.exec_body[0], CtxExprHolder) and if_stmnt.if_branch.exec_body[0].expr == CtxExprLitInt(11, src_loc=ComLoc())

    assert len(if_stmnt.elif_branches) == 1, f"Not exactly 1 elif branch ({if_stmnt.elif_branches})"
    assert if_stmnt.elif_branches[0].cond == CtxExprLitBool(True, src_loc=ComLoc())
    assert isinstance(if_stmnt.elif_branches[0].exec_body[0], CtxExprHolder) and if_stmnt.elif_branches[0].exec_body[0].expr == CtxExprLitInt(22, src_loc=ComLoc())

    assert if_stmnt.else_branch.cond == CtxExprLitBool(True, src_loc=ComLoc())
    assert isinstance(if_stmnt.else_branch.exec_body[0], CtxExprHolder) and if_stmnt.else_branch.exec_body[0].expr == CtxExprLitInt(33, src_loc=ComLoc())


def test_e2h_convert_while_stmnt():
    ast_root = Root(Scope(Stmnt(WhileLoop(ExprLitBool(True), CodeBlock(Stmnt(ExprLitInt(11)))))))

    module = convert(ast_root, Config())

    assert len(module.exec_body) == 1, f"Module does not have exactly one body statement ({str(module.exec_body)})"
    while_loop = module.exec_body[0]
    assert isinstance(while_loop, CtxWhileLoop), f"Module statement is not a CtxWhileLoop, found: ({str(while_loop)})"

    assert while_loop.cond == CtxExprLitBool(True, src_loc=ComLoc())
    assert isinstance(while_loop.exec_body[0], CtxExprHolder) and while_loop.exec_body[0].expr == CtxExprLitInt(11, src_loc=ComLoc())


def test_e2h_convert_var_decl():
    ast_root = Root(
        Scope(
            Stmnt(
                VariableDecl(True, TypeNode("int"), ExprLitIdent("x"), ExprLitInt(42))
            )
        )
    )

    module = convert(ast_root, Config())

    var_x = module.global_var_scope.get_var("x")
    assert var_x is not None, "declared variable is not defined"

    assert var_x.name == "x"
    assert var_x.read_only is True
    assert var_x.var_type == InertType(InertCoreTypes.INT)
    assert var_x.declaration_marker.default_assignment is not None


class TestE2HFuncDecl:

    @pytest.fixture
    def module(self):
        ast_root = Root(
            Scope(
                Stmnt(VariableDecl(True, TypeNode("int"), ExprLitIdent("global_foo"), ExprLitInt(42))),
                FunctionDecl(
                    "add2nums", TypeNode("world"), TypeNode("int"), Scope(CodeBlock(Stmnt(ReturnLn(ExprPlus(ExprLitIdent("a"), ExprLitIdent("b")))))), [], ComLoc(),
                    ParamDecl(ExprLitIdent("a"), TypeNode("int")),
                    ParamDecl(ExprLitIdent("b"), TypeNode("int"), ExprLitInt(0)),
                ),
                FunctionDecl("get42", TypeNode("world"), TypeNode("int"), Scope(CodeBlock(Stmnt(ReturnLn(ExprLitIdent("global_foo"))))), [], ComLoc())
            )
        )

        return convert(ast_root, Config())

    def test_func_exists(self, module: CtxModule):
        add2nums = module.get_function(ExecType(ExecCoreTypes.WORLD, False), "add2nums")
        assert add2nums is not None, "declared function is not defined"

        assert add2nums.get_executor() == ExecType(ExecCoreTypes.WORLD, False)
        assert add2nums.get_name() == "add2nums"
        assert add2nums.get_return_type() == InertType(InertCoreTypes.INT)
        assert len(add2nums.get_params()) == 2
        assert (param_a := add2nums.get_param("a")) is not None and param_a.get_param_type() == InertType(InertCoreTypes.INT)
        assert (param_b := add2nums.get_param("b")) is not None and param_b.get_param_type() == InertType(InertCoreTypes.INT)

    def test_params_in_scope(self, module: CtxModule):
        add2nums = module.get_function(ExecType(ExecCoreTypes.WORLD, False), "add2nums")
        assert add2nums is not None, "declared function is not defined"
        assert isinstance(add2nums, CtxMchyFunc), "mchy func is not instance of mchy func (AbsCtxFunc -> CtxMchyFunc attempted)"

        assert add2nums.func_scope.var_defined("a"), "param a not defined as var"
        assert add2nums.func_scope.var_defined("b"), "param b not defined as var"

        assert (param_a := add2nums.get_param("a")) is not None, "param a unexpectedly un-findable"
        assert (param_b := add2nums.get_param("b")) is not None, "param b unexpectedly un-findable"
        assert add2nums.func_scope.get_var_oerr("a") == param_a.linked_scope_var == CtxVar("a", InertType(InertCoreTypes.INT), True, param_a.linking_decl_mark)
        assert add2nums.func_scope.get_var_oerr("b") == param_b.linked_scope_var == CtxVar("b", InertType(InertCoreTypes.INT), True, param_b.linking_decl_mark)

    def test_func_body_exists_correctly(self, module: CtxModule):
        add2nums = module.get_function(ExecType(ExecCoreTypes.WORLD, False), "add2nums")
        assert add2nums is not None, "declared function is not defined"
        assert isinstance(add2nums, CtxMchyFunc), "mchy func is not instance of mchy func (AbsCtxFunc -> CtxMchyFunc attempted)"

        assert len(add2nums.exec_body) != 0, "Unexpected empty body for function"
        assert len(add2nums.exec_body) == 1, "more than 1 statement in function body"

        stmnt = add2nums.exec_body[0]

        assert isinstance(stmnt, CtxReturn)
        assert stmnt.target == CtxExprPlus(
            CtxExprVar(add2nums.func_scope.get_var_oerr("a"), src_loc=ComLoc()),
            CtxExprVar(add2nums.func_scope.get_var_oerr("b"), src_loc=ComLoc())
        )

    def test_global_var_links(self, module: CtxModule):
        get42 = module.get_function(ExecType(ExecCoreTypes.WORLD, False), "get42")
        assert get42 is not None, "declared function is not defined"
        assert isinstance(get42, CtxMchyFunc), "mchy func is not instance of mchy func (AbsCtxFunc -> CtxMchyFunc attempted)"

        assert len(get42.exec_body) != 0, "Unexpected empty body for function"
        assert len(get42.exec_body) == 1, "more than 1 statement in function body"

        stmnt = get42.exec_body[0]

        assert isinstance(stmnt, CtxReturn)
        assert stmnt.target == CtxExprVar(module.global_var_scope.get_var_oerr("global_foo"), src_loc=ComLoc())


class TestFuncCall1:

    ast_root = Root(Scope(
        FunctionDecl("get42", TypeNode("world"), TypeNode("int"), Scope(CodeBlock(Stmnt(ReturnLn(ExprLitInt(42))))), [], ComLoc()),
        Stmnt(VariableDecl(False, TypeNode("int"), ExprLitIdent("foo"), ExprFuncCall(ExprLitWorld(None), ExprLitIdent("get42")))),
    ))

    def test_calling_declared_function(self):
        module = convert(TestFuncCall1.ast_root, Config())

        decl_var_mark = module.exec_body[1]
        assert isinstance(decl_var_mark, MarkerDeclVar)
        assert decl_var_mark.default_assignment is not None, "defined default assignment missing"
        rhs_expr = decl_var_mark.default_assignment.rhs
        assert isinstance(rhs_expr, CtxExprFuncCall)
        assert rhs_expr.function == module.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "get42")

    def test_mchy_function_called_before_declaration(self):
        flipped_root = Root(Scope(
            *list(reversed(TestFuncCall1.ast_root.children[0].children))  # Reverse stmnt order of above test
        ))
        with pytest.raises(ConversionError):
            convert(flipped_root, Config())


def test_nested_calls():
    ast_root = Root(Scope(
        FunctionDecl("get42", TypeNode("world"), TypeNode("int"), Scope(CodeBlock(Stmnt(ReturnLn(ExprLitInt(42))))), [], ComLoc()),
        FunctionDecl(
            "get42from_get42", TypeNode("world"), TypeNode("int"), Scope(CodeBlock(Stmnt(ReturnLn(ExprFuncCall(ExprLitThis(None), ExprLitIdent("get42")))))), [], ComLoc()
        ),
        Stmnt(VariableDecl(False, TypeNode("int"), ExprLitIdent("foo"), ExprFuncCall(ExprLitWorld(None), ExprLitIdent("get42from_get42")))),
    ))
    module = convert(ast_root, Config())

    func2 = module.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "get42from_get42")
    assert isinstance(func2, CtxMchyFunc), "defined mchy function is not mchy function"
    return_ln = func2.exec_body[0]
    assert isinstance(return_ln, CtxReturn)
    expr_func_call = return_ln.target
    assert isinstance(expr_func_call, CtxExprFuncCall)
    assert expr_func_call.function == module.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "get42")


def test_ticking_func_registered():
    ast_root = Root(Scope(
        FunctionDecl("main_tick", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [Decorator(ExprLitIdent("ticking"))], ComLoc()),
    ))

    module = convert(ast_root, Config())

    assert module.get_ticking_funcs() == [module.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "main_tick")]


def test_public_func_registered():
    ast_root = Root(Scope(
        FunctionDecl("give_apple", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [Decorator(ExprLitIdent("public"))], ComLoc()),
    ))

    module = convert(ast_root, Config())

    assert module.get_public_funcs() == [module.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "give_apple")]
