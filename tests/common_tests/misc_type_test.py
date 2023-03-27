
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from tests.common_tests.helpers import BOOL, INT, FLOAT, STR

import pytest


@pytest.mark.parametrize("left_type, right_type, expectation", [
    (InertType(INT), InertType(INT), True),
    (InertType(INT), InertType(BOOL), False),
    (InertType(INT), InertType(INT, const=True), False),
    (InertType(INT, const=True), InertType(INT), False),
    (InertType(INT), InertType(INT, nullable=True), False),
    (InertType(INT, nullable=True), InertType(INT), False),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.WORLD, False), True),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.WORLD, False), False),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.ENTITY, False), True),
    (ExecType(ExecCoreTypes.ENTITY, True), ExecType(ExecCoreTypes.ENTITY, False), False),
])
def test_node_eq(left_type: ComType, right_type: ComType, expectation: bool):
    assert (left_type == right_type) == expectation


def test_null_nullable():
    assert (InertType(InertCoreTypes.NULL).nullable is False), "Null is nullable (The distinction is important for cmd optimizers)"
