
from typing import Union
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertType, TypeUnion, matches_type
from tests.common_tests.helpers import NULL, BOOL, INT, FLOAT, STR

import pytest


@pytest.mark.parametrize("guard_type, challenge_type, expected_result", [
    # Inert types
    (InertType(INT), InertType(INT), True),
    (InertType(STR), InertType(INT), False),
    (InertType(INT), InertType(STR), False),
    (InertType(INT), InertType(BOOL), True),
    (InertType(INT), InertType(FLOAT), False),
    (InertType(BOOL), InertType(INT), False),
    (InertType(FLOAT), InertType(INT), True),
    (InertType(FLOAT, const=True), InertType(INT, const=True), True),
    (InertType(INT, const=True), InertType(INT), False),
    (InertType(INT), InertType(INT, const=True), True),
    (InertType(INT, nullable=True), InertType(INT), True),
    (InertType(INT), InertType(INT, nullable=True), False),
    (InertType(INT, nullable=True), InertType(NULL, const=True), True),
    (InertType(INT, const=True), InertType(INT, nullable=True), False),

    # World Exec
    (ExecType(ExecCoreTypes.WORLD, False), InertType(INT), False),
    (ExecType(ExecCoreTypes.WORLD, False), InertType(BOOL), False),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.WORLD, False), True),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.ENTITY, False), True),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.ENTITY, True), True),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.PLAYER, False), True),
    (ExecType(ExecCoreTypes.WORLD, False), ExecType(ExecCoreTypes.PLAYER, True), True),

    # Entity Exec
    (ExecType(ExecCoreTypes.ENTITY, False), InertType(INT), False),
    (ExecType(ExecCoreTypes.ENTITY, False), InertType(BOOL), False),
    (ExecType(ExecCoreTypes.ENTITY, True), InertType(INT), False),
    (ExecType(ExecCoreTypes.ENTITY, True), InertType(BOOL), False),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.ENTITY, False), True),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.ENTITY, True), False),
    (ExecType(ExecCoreTypes.ENTITY, True), ExecType(ExecCoreTypes.ENTITY, False), True),
    (ExecType(ExecCoreTypes.ENTITY, True), ExecType(ExecCoreTypes.ENTITY, True), True),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.PLAYER, False), True),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.PLAYER, True), False),
    (ExecType(ExecCoreTypes.ENTITY, True), ExecType(ExecCoreTypes.PLAYER, False), True),
    (ExecType(ExecCoreTypes.ENTITY, True), ExecType(ExecCoreTypes.PLAYER, True), True),
    (ExecType(ExecCoreTypes.ENTITY, False), ExecType(ExecCoreTypes.WORLD, False), False),

    # Player Exec
    (ExecType(ExecCoreTypes.PLAYER, False), InertType(INT), False),
    (ExecType(ExecCoreTypes.PLAYER, False), InertType(BOOL), False),
    (ExecType(ExecCoreTypes.PLAYER, True), InertType(INT), False),
    (ExecType(ExecCoreTypes.PLAYER, True), InertType(BOOL), False),
    (ExecType(ExecCoreTypes.PLAYER, False), ExecType(ExecCoreTypes.PLAYER, False), True),
    (ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.PLAYER, False), True),
    (ExecType(ExecCoreTypes.PLAYER, False), ExecType(ExecCoreTypes.PLAYER, True), False),
    (ExecType(ExecCoreTypes.PLAYER, False), ExecType(ExecCoreTypes.ENTITY, False), False),
    (ExecType(ExecCoreTypes.PLAYER, False), ExecType(ExecCoreTypes.ENTITY, True), False),
    (ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False), False),
    (ExecType(ExecCoreTypes.PLAYER, False), ExecType(ExecCoreTypes.WORLD, False), False),

    # Inert Unions
    (TypeUnion(InertType(INT), InertType(STR)), InertType(INT), True),
    (TypeUnion(InertType(INT), InertType(STR)), InertType(FLOAT), False),
    (TypeUnion(InertType(INT), InertType(STR)), ExecType(ExecCoreTypes.PLAYER, False), False),
    (TypeUnion(InertType(INT), InertType(STR)), ExecType(ExecCoreTypes.WORLD, False), False),

    # Exec Unions
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), InertType(INT), False),
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), ExecType(ExecCoreTypes.PLAYER, False), True),
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), ExecType(ExecCoreTypes.PLAYER, True), True),
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), ExecType(ExecCoreTypes.ENTITY, False), True),
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), ExecType(ExecCoreTypes.ENTITY, True), False),
    (TypeUnion(ExecType(ExecCoreTypes.PLAYER, True), ExecType(ExecCoreTypes.ENTITY, False)), ExecType(ExecCoreTypes.WORLD, False), False),

    # Mixed Unions
    (TypeUnion(InertType(STR, const=True), InertType(FLOAT, const=True), InertType(INT), InertType(BOOL), InertType(NULL)), ExecType(ExecCoreTypes.ENTITY, True), False),
    (TypeUnion(InertType(STR, const=True), InertType(FLOAT, const=True), InertType(INT), InertType(BOOL), InertType(NULL)), ExecType(ExecCoreTypes.ENTITY, False), False),
    (TypeUnion(InertType(STR, const=True), InertType(FLOAT, const=True), InertType(INT), InertType(BOOL), InertType(NULL)), ExecType(ExecCoreTypes.WORLD, False), False),
    (TypeUnion(InertType(STR, const=True), InertType(FLOAT, const=True), InertType(INT), InertType(BOOL), InertType(NULL)), InertType(INT), True),
])
def test_matches_types(guard_type: Union[TypeUnion, ComType], challenge_type: ComType, expected_result: bool):
    assert (matches_type(guard_type, challenge_type) == expected_result)
