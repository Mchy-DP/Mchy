from mchy.mchy_ast.nodes import *

import pytest


@pytest.mark.parametrize("left, right, expectation, failure_explanation", [
    (Root(), Root(), True, "Empty roots unequal?"),
    (Root(ExprLitInt(42)), Root(), False, "Extra child equal?"),
    (Root(Stmnt(ExprLitInt(13))), Root(Stmnt(ExprLitInt(42))), False, "Nested mismatches spotted"),
    (ExprLitInt(42), ExprLitInt(42), True, "Identical literals differ"),
    (ExprLitInt(13), ExprLitInt(42), False, "Different ints compare equal"),
    (TypeNode("int"), TypeNode("int"), True, None),
    (TypeNode("int", group=True), TypeNode("int"), False, None),
    (TypeNode("int", compile_const=True), TypeNode("int"), False, None),
    (TypeNode("int", nullable=True), TypeNode("int"), False, None),
    (TypeNode("int"), TypeNode("int", group=True), False, None),
    (TypeNode("int", group=True), TypeNode("int", group=True), True, None),
    (TypeNode("int", compile_const=True), TypeNode("int", group=True), False, None),
    (TypeNode("int", nullable=True), TypeNode("int", group=True), False, None),
])
def test_node_eq(left: Node, right: Node, expectation: bool, failure_explanation: Optional[str]):
    if failure_explanation is None:
        assert (left == right) == expectation
    else:
        assert (left == right) == expectation, failure_explanation
