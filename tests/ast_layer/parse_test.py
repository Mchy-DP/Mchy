
from mchy.common.config import Config
from mchy.mchy_ast.convert_parse import mchy_parse

from mchy.mchy_ast.nodes import *

import pytest

from tests.helpers.render_trees import render_diff, render_tree


_TEST_CONFIG = Config()


@pytest.mark.parametrize("expression, expected_tree", [
    # simple Maths
    ("42", Root(Scope(Stmnt(ExprLitInt(42))))),
    ("42 ", Root(Scope(Stmnt(ExprLitInt(42))))),
    (" 42", Root(Scope(Stmnt(ExprLitInt(42))))),
    ("\n42", Root(Scope(Stmnt(ExprLitInt(42))))),
    ("null", Root(Scope(Stmnt(ExprLitNull(None))))),
    ("this", Root(Scope(Stmnt(ExprLitThis(None))))),
    ("world", Root(Scope(Stmnt(ExprLitWorld(None))))),
    ("true", Root(Scope(Stmnt(ExprLitBool(True))))),
    ("True", Root(Scope(Stmnt(ExprLitBool(True))))),
    ("false", Root(Scope(Stmnt(ExprLitBool(False))))),
    ("False", Root(Scope(Stmnt(ExprLitBool(False))))),
    ("return 42", Root(Scope(Stmnt(ReturnLn(ExprLitInt(42)))))),
    ("-42", Root(Scope(Stmnt(ExprMinus(ExprLitInt(0), ExprLitInt(42)))))),
    ("42.13", Root(Scope(Stmnt(ExprLitFloat(42.13))))),
    ("42\n13", Root(Scope(Stmnt(ExprLitInt(42)), Stmnt(ExprLitInt(13))))),
    ("'foo'", Root(Scope(Stmnt(ExprLitStr("foo"))))),
    ('"foo"', Root(Scope(Stmnt(ExprLitStr("foo"))))),
    ('"bad ` char"', Root(Scope(Stmnt(ExprLitStr("bad ` char"))))),
    ("\"Hi! I'm Dave$;s\"", Root(Scope(Stmnt(ExprLitStr("Hi! I'm Dave$;s"))))),
    (r'''"DBQ escape\" me!"''', Root(Scope(Stmnt(ExprLitStr(r"""DBQ escape" me!"""))))),
    (r'''"DBQ2 escape\"\' me!"''', Root(Scope(Stmnt(ExprLitStr(r"""DBQ2 escape"\' me!"""))))),
    (r"""'SGQ escape\"\' me!'""", Root(Scope(Stmnt(ExprLitStr(r"""SGQ escape\"' me!"""))))),
    (r'''"DBQ-tail escape me!\""''', Root(Scope(Stmnt(ExprLitStr(r'''DBQ-tail escape me!"'''))))),
    ("3+8", Root(Scope(Stmnt(ExprPlus(ExprLitInt(3), ExprLitInt(8)))))),
    ("3 + 8", Root(Scope(Stmnt(ExprPlus(ExprLitInt(3), ExprLitInt(8)))))),
    ("3 +\n 8", Root(Scope(Stmnt(ExprPlus(ExprLitInt(3), ExprLitInt(8)))))),
    ("3-8", Root(Scope(Stmnt(ExprMinus(ExprLitInt(3), ExprLitInt(8)))))),
    ("4/2", Root(Scope(Stmnt(ExprDiv(ExprLitInt(4), ExprLitInt(2)))))),
    ("19%7", Root(Scope(Stmnt(ExprMod(ExprLitInt(19), ExprLitInt(7)))))),
    ("2-3*8", Root(Scope(Stmnt(ExprMinus(ExprLitInt(2), ExprMult(ExprLitInt(3), ExprLitInt(8))))))),
    ("(2-3)*8", Root(Scope(Stmnt(ExprMult(ExprMinus(ExprLitInt(2), ExprLitInt(3)), ExprLitInt(8)))))),
    ("4^3", Root(Scope(Stmnt(ExprExponent(ExprLitInt(4), ExprLitInt(3)))))),
    ("4**3", Root(Scope(Stmnt(ExprExponent(ExprLitInt(4), ExprLitInt(3)))))),
    # bonus simple
    ("foo", Root(Scope(Stmnt(ExprLitIdent("foo"))))),
    ("foo = 42", Root(Scope(Stmnt(Assignment(ExprLitIdent("foo"), ExprLitInt(42)))))),
    ("foo = (\n\n42\n\n)", Root(Scope(Stmnt(Assignment(ExprLitIdent("foo"), ExprLitInt(42)))))),
    ("# Test comment", Root(Scope(Stmnt(UserComment("# Test comment"))))),
    ("4 ?? 3", Root(Scope(Stmnt(ExprNullCoal(ExprLitInt(4), ExprLitInt(3)))))),
    # complex rules
    ("this.jump()", Root(Scope(Stmnt(ExprFuncCall(ExprLitThis(None), ExprLitIdent("jump")))))),
    ("world.sleep(1)", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("sleep"), ExprFragParam(value=ExprLitInt(1))))))),
    ("sleep(1)", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("sleep"), ExprFragParam(value=ExprLitInt(1))))))),
    ("sleep(\n\n1\n\n)", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("sleep"), ExprFragParam(value=ExprLitInt(1))))))),
    ("sleep(\n\n1,\n2,\n\n)", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("sleep"), ExprFragParam(value=ExprLitInt(1)), ExprFragParam(value=ExprLitInt(2))))))),
    ("world.sleep(duration=1)", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("sleep"), ExprFragParam(value=ExprLitInt(1), label=ExprLitIdent("duration"))))))),
    ("world.get_players().find()", Root(Scope(Stmnt(ExprFuncCall(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("get_players")), ExprLitIdent("find")))))),
    ("math.sum(1,2)", Root(Scope(Stmnt(ExprFuncCall(ExprLitIdent("math"), ExprLitIdent("sum"), ExprFragParam(value=ExprLitInt(1)), ExprFragParam(value=ExprLitInt(2))))))),
    ("this.name", Root(Scope(Stmnt(ExprPropertyAccess(ExprLitThis(None), ExprLitIdent("name")))))),
    ("this.passenger.name", Root(Scope(Stmnt(ExprPropertyAccess(ExprPropertyAccess(ExprLitThis(None), ExprLitIdent("passenger")), ExprLitIdent("name")))))),
    ("world.colors.red", Root(Scope(Stmnt(ExprPropertyAccess(ExprPropertyAccess(ExprLitWorld(None), ExprLitIdent("colors")), ExprLitIdent("red")))))),
    # raw cmd
    ("/say hi", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    ("  /say hi", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    ("/say hi\n", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    ("  /say hi\n", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    ("\n/say hi", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    ("\n  /say hi", Root(Scope(Stmnt(ExprFuncCall(ExprLitWorld(None), ExprLitIdent("cmd"), ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr("/say hi"))))))),
    # variable declaration
    ("var foo: int", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int"), ExprLitIdent("foo")))))),
    ("var foo: int = 5", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int"), ExprLitIdent("foo"), ExprLitInt(5)))))),
    ("let foo: int = 42", Root(Scope(Stmnt(VariableDecl(True, TypeNode("int"), ExprLitIdent("foo"), ExprLitInt(42)))))),
    ("var foo: int!", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int", compile_const=True), ExprLitIdent("foo")))))),
    ("var foo: int?", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int", nullable=True), ExprLitIdent("foo")))))),
    ("var foo: Group[Entity]", Root(Scope(Stmnt(VariableDecl(False, TypeNode("Entity", group=True), ExprLitIdent("foo")))))),
    ("var foo: world", Root(Scope(Stmnt(VariableDecl(False, TypeNode("world", group=False), ExprLitIdent("foo")))))),
    ("var foo: int? = 5", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int", nullable=True), ExprLitIdent("foo"), ExprLitInt(5)))))),
    ("var foo: int? = null", Root(Scope(Stmnt(VariableDecl(False, TypeNode("int", nullable=True), ExprLitIdent("foo"), ExprLitNull(None)))))),
    ("var foo: null = null", Root(Scope(Stmnt(VariableDecl(False, TypeNode("null"), ExprLitIdent("foo"), ExprLitNull(None)))))),
    # function decl
    ("def world func1(){}", Root(Scope(FunctionDecl("func1", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [], ComLoc())))),
    ("def world func1(p1: int){}", Root(Scope(
        FunctionDecl("func1", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [], ComLoc(), ParamDecl(ExprLitIdent("p1"), TypeNode("int")))
    ))),
    ("def Group[Entity] func1() -> int{}", Root(Scope(FunctionDecl("func1", TypeNode("Entity", group=True), TypeNode("int"), Scope(CodeBlock()), [], ComLoc())))),
    ("def world func1(){42}", Root(Scope(FunctionDecl("func1", TypeNode("world"), TypeNode("null"), Scope(CodeBlock(Stmnt(ExprLitInt(42)))), [], ComLoc())))),
    ("def func1(){}", Root(Scope(FunctionDecl("func1", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [], ComLoc())))),
    ("11\ndef func1(){\n22\n}\n33", Root(Scope(
        Stmnt(ExprLitInt(11)),
        FunctionDecl("func1", TypeNode("world"), TypeNode("null"), Scope(CodeBlock(Stmnt(ExprLitInt(22)))), [], ComLoc()),
        Stmnt(ExprLitInt(33))
        ))),
    ("@ticking\ndef mn_tick(){}", Root(Scope(FunctionDecl("mn_tick", TypeNode("world"), TypeNode("null"), Scope(CodeBlock()), [Decorator(ExprLitIdent("ticking"))], ComLoc())))),
    # If
    ("if True{42}", Root(Scope(Stmnt(IfStruct(ExprLitBool(True), CodeBlock(Stmnt(ExprLitInt(42)))))))),
    ("if (True){42}", Root(Scope(Stmnt(IfStruct(ExprLitBool(True), CodeBlock(Stmnt(ExprLitInt(42)))))))),
    ("if (False){}", Root(Scope(Stmnt(IfStruct(ExprLitBool(False), CodeBlock()))))),
    ("if (False){} elif(True){13}", Root(Scope(Stmnt(IfStruct(ExprLitBool(False), CodeBlock(), ElifStruct(ExprLitBool(True), CodeBlock(Stmnt(ExprLitInt(13))))))))),
    ("if (False){} elif(True){} elif(False){}", Root(Scope(Stmnt(
        IfStruct(ExprLitBool(False), CodeBlock(), ElifStruct(ExprLitBool(True), CodeBlock(), ElifStruct(ExprLitBool(False), CodeBlock())))
    )))),
    ("if (False){} elif(True){} else{32}", Root(Scope(Stmnt(
        IfStruct(ExprLitBool(False), CodeBlock(), ElifStruct(ExprLitBool(True), CodeBlock()), ElseStruct(CodeBlock(Stmnt(ExprLitInt(32)))))
    )))),
    ("if (False){} else{76}", Root(Scope(Stmnt(IfStruct(ExprLitBool(False), CodeBlock(), None, ElseStruct(CodeBlock(Stmnt(ExprLitInt(76))))))))),
    ("if (x) {\nx = 10\n}", Root(Scope(Stmnt(IfStruct(ExprLitIdent("x"), CodeBlock(Stmnt(Assignment(ExprLitIdent("x"), ExprLitInt(10))))))))),
    ("if (x) {x = 10\n\n}", Root(Scope(Stmnt(IfStruct(ExprLitIdent("x"), CodeBlock(Stmnt(Assignment(ExprLitIdent("x"), ExprLitInt(10))))))))),
    ("if x {x}", Root(Scope(Stmnt(IfStruct(ExprLitIdent("x"), CodeBlock(Stmnt(ExprLitIdent("x")))))))),
    # While
    ("while True{}", Root(Scope(Stmnt(WhileLoop(ExprLitBool(True), CodeBlock()))))),
    ("while x {x = x - 1}", Root(Scope(Stmnt(WhileLoop(ExprLitIdent("x"), CodeBlock(Stmnt(Assignment(ExprLitIdent("x"), ExprMinus(ExprLitIdent("x"), ExprLitInt(1)))))))))),
    # For
    ("for x in 0..5 {}", Root(Scope(Stmnt(ForLoop(ExprLitIdent("x"), ExprLitInt(0), ExprLitInt(5), CodeBlock()))))),
    ("for x in 0..5 {11}", Root(Scope(Stmnt(ForLoop(ExprLitIdent("x"), ExprLitInt(0), ExprLitInt(5), CodeBlock(Stmnt(ExprLitInt(11)))))))),
    ("for x in a..b {}", Root(Scope(Stmnt(ForLoop(ExprLitIdent("x"), ExprLitIdent("a"), ExprLitIdent("b"), CodeBlock()))))),
    ("for x in 0..(b+1) {}", Root(Scope(Stmnt(ForLoop(ExprLitIdent("x"), ExprLitInt(0), ExprPlus(ExprLitIdent("b"), ExprLitInt(1)), CodeBlock()))))),
    # Relation Operations
    ("42 == 42", Root(Scope(Stmnt(ExprEquality(ExprLitInt(42), ExprLitInt(42)))))),
    ("42 != 42", Root(Scope(Stmnt(ExprInequality(ExprLitInt(42), ExprLitInt(42)))))),
    ("42 >= 42", Root(Scope(Stmnt(ExprCompGTE(ExprLitInt(42), ExprLitInt(42)))))),
    ("42 >  42", Root(Scope(Stmnt(ExprCompGT(ExprLitInt(42), ExprLitInt(42)))))),
    ("42 <= 42", Root(Scope(Stmnt(ExprCompLTE(ExprLitInt(42), ExprLitInt(42)))))),
    ("42 <  42", Root(Scope(Stmnt(ExprCompLT(ExprLitInt(42), ExprLitInt(42)))))),
    ("x + 1 > 15", Root(Scope(Stmnt(ExprCompGT(ExprPlus(ExprLitIdent("x"), ExprLitInt(1)), ExprLitInt(15)))))),
    # Not, And, Or
    ("not true", Root(Scope(Stmnt(ExprNot(ExprLitBool(True)))))),
    ("not false", Root(Scope(Stmnt(ExprNot(ExprLitBool(False)))))),
    ("true and true", Root(Scope(Stmnt(ExprAnd(ExprLitBool(True), ExprLitBool(True)))))),
    ("true or true", Root(Scope(Stmnt(ExprOr(ExprLitBool(True), ExprLitBool(True)))))),
    ("false and false", Root(Scope(Stmnt(ExprAnd(ExprLitBool(False), ExprLitBool(False)))))),
    ("false or false", Root(Scope(Stmnt(ExprOr(ExprLitBool(False), ExprLitBool(False)))))),
    # Inclusion
    ("include './test.txt' at tags.blocks", Root(Scope(Include(ExprLitStr("./test.txt"), ExprLitIdent("tags"), ExprLitIdent("blocks")))))
])
def test_tree_matches(expression: str, expected_tree: Root):
    root_node: Root = mchy_parse(expression, _TEST_CONFIG)
    print("Full Tree:\n"+render_tree(root_node))
    assert root_node == expected_tree, "AST does not match expected:\n" + render_diff(root_node, expected_tree, True)
