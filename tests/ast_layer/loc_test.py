from typing import List, Tuple, Type

import pytest
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.mchy_ast.convert_parse import mchy_parse

from mchy.mchy_ast.nodes import *
from tests.helpers.diff_locs import loc_diff
from tests.helpers.render_trees import render_tree


_TEST_CONFIG = Config()


@pytest.mark.parametrize("code, path, loc", [
    ("var x: int = 3", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(1, 0, 1, 14)),
    ("var x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(1, 0, 1, 16)),
    ("\nvar x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(2, 0, 2, 16)),
    ("\n\nvar x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(3, 0, 3, 16)),
    ("    var x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(1, 4, 1, 20)),
    ("var x: int = (300)", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(1, 0, 1, 18)),
    ("var x: int = (\n300\n)", [(Root, 0), (Scope, 0), (Stmnt, None)], ComLoc(1, 0, 3, 1)),
    ("var x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, None)], ComLoc(1, 0, 1, 16)),
    ("var x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 0), (TypeNode, None)], ComLoc(1, 7, 1, 10)),
    ("var x: int = 300", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 16)),
    ("var x: int = 'str'", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 18)),
    ('var x: int = "str"', [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3.14", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 17)),
    ("var x: int = null", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 17)),
    ("var x: int = world", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = this", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 17)),
    ("var x: int = true", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 17)),
    ("var x: int = foo", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprGen, None)], ComLoc(1, 13, 1, 16)),
    ("var x: int = 3 ?? 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprNullCoal, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 or 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprOr, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 and 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprAnd, None)], ComLoc(1, 13, 1, 20)),
    ("var x: int = not 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprNot, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 == 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprEquality, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 != 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprInequality, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 > 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprCompGT, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 >= 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprCompGTE, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 < 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprCompLT, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 <= 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprCompLTE, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = 3 + 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprPlus, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 - 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprMinus, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 * 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprMult, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 / 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprDiv, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 % 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprMod, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 ^ 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprExponent, None)], ComLoc(1, 13, 1, 18)),
    ("var x: int = 3 ** 4", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprExponent, None)], ComLoc(1, 13, 1, 19)),
    ("var x: int = -42", [(Root, 0), (Scope, 0), (Stmnt, 0), (VariableDecl, 1), (ExprMinus, None)], ComLoc(1, 13, 1, 16)),
    ("world", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprLitWorld, None)], ComLoc(1, 0, 1, 5)),
    ("world.prop", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprPropertyAccess, None)], ComLoc(1, 0, 1, 10)),
    ("world.prop", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprPropertyAccess, 0), (ExprLitWorld, None)], ComLoc(1, 0, 1, 5)),
    ("world.prop", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprPropertyAccess, 1), (ExprLitIdent, None)], ComLoc(1, 6, 1, 10)),
    ("world.func()", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, None)], ComLoc(1, 0, 1, 12)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, None)], ComLoc(1, 0, 1, 15)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 0), (ExprLitWorld, None)], ComLoc(1, 0, 1, 5)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 1), (ExprLitIdent, None)], ComLoc(1, 6, 1, 10)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 2), (ExprFragParam, None)], ComLoc(1, 11, 1, 12)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 2), (ExprFragParam, 0), (ExprLitInt, None)], ComLoc(1, 11, 1, 12)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 3), (ExprFragParam, None)], ComLoc(1, 13, 1, 14)),
    ("world.func(3,4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 3), (ExprFragParam, 0), (ExprLitInt, None)], ComLoc(1, 13, 1, 14)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, None)], ComLoc(1, 0, 1, 20)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 0), (ExprLitWorld, None)], ComLoc(1, 0, 1, 5)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 1), (ExprLitIdent, None)], ComLoc(1, 6, 1, 10)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 2), (ExprFragParam, None)], ComLoc(1, 11, 1, 14)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 2), (ExprFragParam, 0), (ExprLitIdent, None)], ComLoc(1, 11, 1, 12)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 2), (ExprFragParam, 1), (ExprLitInt, None)], ComLoc(1, 13, 1, 14)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 3), (ExprFragParam, None)], ComLoc(1, 16, 1, 19)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 3), (ExprFragParam, 0), (ExprLitIdent, None)], ComLoc(1, 16, 1, 17)),
    ("world.func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 3), (ExprFragParam, 1), (ExprLitInt, None)], ComLoc(1, 18, 1, 19)),
    ("func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, None)], ComLoc(1, 0, 1, 14)),
    ("func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 0), (ExprLitWorld, None)], ComLoc(None, None, None, None)),
    ("func(a=3, b=4)", [(Root, 0), (Scope, 0), (Stmnt, 0), (ExprFuncCall, 1), (ExprLitIdent, None)], ComLoc(1, 0, 1, 4)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, None)], ComLoc(1, 0, 3, 1)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 0), (TypeNode, None)], ComLoc(None, None, None, None)),  # exec type
    ("def Player foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 0), (TypeNode, None)], ComLoc(1, 4, 1, 10)),  # exec type
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 1), (TypeNode, None)], ComLoc(None, None, None, None)),  # return type
    ("def foo(a: int, b: int = 13) -> int {\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 1), (TypeNode, None)], ComLoc(1, 32, 1, 35)),  # return type
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 2), (Scope, None)], ComLoc(1, 28, 3, 1)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 2), (Scope, 0), (CodeBlock, None)], ComLoc(1, 28, 3, 1)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 2), (Scope, 0), (CodeBlock, 0), (Stmnt, None)], ComLoc(2, 0, 2, 2)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 2), (Scope, 0), (CodeBlock, 0), (Stmnt, 0), (ExprLitInt, None)], ComLoc(2, 0, 2, 2)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 3), (ParamDecl, None)], ComLoc(1, 8, 1, 14)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 3), (ParamDecl, 0), (ExprLitIdent, None)], ComLoc(1, 8, 1, 9)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 3), (ParamDecl, 1), (TypeNode, None)], ComLoc(1, 11, 1, 14)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 4), (ParamDecl, None)], ComLoc(1, 16, 1, 27)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 4), (ParamDecl, 0), (ExprLitIdent, None)], ComLoc(1, 16, 1, 17)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 4), (ParamDecl, 1), (TypeNode, None)], ComLoc(1, 19, 1, 22)),
    ("def foo(a: int, b: int = 13){\n42\n}", [(Root, 0), (Scope, 0), (FunctionDecl, 4), (ParamDecl, 2), (ExprLitInt, None)], ComLoc(1, 25, 1, 27)),
    ("@ticking\ndef main_tick(){}", [(Root, 0), (Scope, 0), (FunctionDecl, None)], ComLoc(1, 0, 2, 17)),
    ("@ticking\ndef main_tick(){}", [(Root, 0), (Scope, 0), (FunctionDecl, 3), (Decorator, None)], ComLoc(1, 0, 1, 8)),
    ("@ticking\ndef main_tick(){}", [(Root, 0), (Scope, 0), (FunctionDecl, 3), (Decorator, 0), (ExprLitIdent, None)], ComLoc(1, 1, 1, 8)),
    ("# I am a comment!", [(Root, 0), (Scope, 0), (Stmnt, 0), (UserComment, None)], ComLoc(1, 0, 1, 17)),
    ("return 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (ReturnLn, None)], ComLoc(1, 0, 1, 9)),
    ("return 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (ReturnLn, 0), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("foo = 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, None)], ComLoc(1, 0, 1, 8)),
    ("foo = 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo = 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprLitInt, None)], ComLoc(1, 6, 1, 8)),
    ("foo += 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprPlus, None)], ComLoc(1, 0, 1, 9)),
    ("foo += 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprPlus, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo += 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprPlus, 1), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("foo -= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMinus, None)], ComLoc(1, 0, 1, 9)),
    ("foo -= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMinus, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo -= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMinus, 1), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("foo *= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMult, None)], ComLoc(1, 0, 1, 9)),
    ("foo *= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMult, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo *= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMult, 1), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("foo /= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprDiv, None)], ComLoc(1, 0, 1, 9)),
    ("foo /= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprDiv, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo /= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprDiv, 1), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("foo %= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMod, None)], ComLoc(1, 0, 1, 9)),
    ("foo %= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMod, 0), (ExprLitIdent, None)], ComLoc(1, 0, 1, 3)),
    ("foo %= 15", [(Root, 0), (Scope, 0), (Stmnt, 0), (Assignment, 1), (ExprMod, 1), (ExprLitInt, None)], ComLoc(1, 7, 1, 9)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, None)], ComLoc(1, 0, 1, 33)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 0), (ExprLitIdent, None)], ComLoc(1, 3, 1, 5)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 1), (CodeBlock, None)], ComLoc(1, 6, 1, 10)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 2), (ElifStruct, None)], ComLoc(1, 11, 1, 23)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 2), (ElifStruct, 0), (ExprLitIdent, None)], ComLoc(1, 16, 1, 18)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 2), (ElifStruct, 1), (CodeBlock, None)], ComLoc(1, 19, 1, 23)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 3), (ElseStruct, None)], ComLoc(1, 24, 1, 33)),
    ("if x1 {11} elif x2 {22} else {33}", [(Root, 0), (Scope, 0), (Stmnt, 0), (IfStruct, 3), (ElseStruct, 0), (CodeBlock, None)], ComLoc(1, 29, 1, 33)),
    ("for foo in 0..x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (ForLoop, None)], ComLoc(1, 0, 1, 19)),
    ("for foo in 0..x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (ForLoop, 0), (ExprLitIdent, None)], ComLoc(1, 4, 1, 7)),
    ("for foo in 0..x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (ForLoop, 1), (ExprLitInt, None)], ComLoc(1, 11, 1, 12)),
    ("for foo in 0..x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (ForLoop, 2), (ExprLitIdent, None)], ComLoc(1, 14, 1, 15)),
    ("for foo in 0..x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (ForLoop, 3), (CodeBlock, None)], ComLoc(1, 16, 1, 19)),
    ("while x {1}", [(Root, 0), (Scope, 0), (Stmnt, 0), (WhileLoop, None)], ComLoc(1, 0, 1, 11)),
])
def test_loc_expected(code: str, path: List[Tuple[Type[Node], Optional[int]]], loc: ComLoc):
    root_node: Root = mchy_parse(code, _TEST_CONFIG)
    active_node: Node = root_node
    for node_type, child_index in path:
        assert isinstance(active_node, node_type), "AST not in expected structure, tree:\n" + render_tree(root_node)
        if child_index is not None:
            active_node = active_node.children[child_index]
    if child_index is not None:
        raise ValueError("Test malformed: Requested Path in testing does not end with None")
    assert active_node.loc == loc, (
        f"Location mismatch for code {repr(code)} and route:\n" +
        f" >  [{', '.join([f'({nt.__name__}, {ci})' for nt,ci in path])}]\n" +
        f" >  Location Diff: " + loc_diff(active_node.loc, loc)
    )


def test_func_def_loc1():
    root_node: Root = mchy_parse("""@public\ndef foo(){}""", _TEST_CONFIG)
    func_decl = root_node.children[0].children[0]
    assert isinstance(func_decl, FunctionDecl), "Tree doesn't match:\n" + render_tree(root_node)
    expected_loc = ComLoc(2, 0, 2, 3)
    assert func_decl.def_loc == expected_loc, "Location Diff: " + loc_diff(func_decl.def_loc, expected_loc)


def test_func_def_loc2():
    root_node: Root = mchy_parse("""@public\ndef foo1(){}\n@public\ndef foo2(){}""", _TEST_CONFIG)
    func_decl = root_node.children[0].children[1]
    assert isinstance(func_decl, FunctionDecl), "Tree doesn't match:\n" + render_tree(root_node)
    expected_loc = ComLoc(4, 0, 4, 3)
    assert func_decl.def_loc == expected_loc, "Location Diff: " + loc_diff(func_decl.def_loc, expected_loc)
