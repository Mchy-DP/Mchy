from mchy.mchy_ast.nodes import *

import pytest


def test_deeper_clone():
    original = Root(Stmnt(ExprLitInt(42)))
    new = original.clone()

    assert id(new) != id(original), "Clone returned same object"
    assert id(new.children[0].children[0]) != id(original.children[0].children[0]), "Clone did not deep copy"
    assert new.children[0].children[0].value == original.children[0].children[0].value, "Clone did not preserve value property"
    assert new == original, "Clone returned non-equal nodes"


@pytest.mark.parametrize("original", [
    Root(),
    VariableDecl(False, TypeNode("int"), ExprLitIdent("foo")),
    TypeNode("int"),
    TypeNode("int", group=True),
    TypeNode("int", compile_const=True),
    TypeNode("int", nullable=True),
])
def test_mass_clone(original: Node):
    new = original.clone()

    assert id(new) != id(original), "Clone returned same object"
    assert new == original, "Clone returned non-equal nodes"
