from typing import Optional
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.config import Config
from mchy.contextual.struct.module import CtxModule
from mchy.library.std.struct_pos import StructPos
from mchy.mchy_ast.nodes import TypeNode
from mchy.contextual.generation import convert_explicit_type
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.errors import ConversionError

import pytest

_MODULE = CtxModule(Config())
_MODULE.import_ns(Namespace.get_namespace("std"))


@pytest.mark.parametrize("ast, expected_ctype", [
    # Inert target correct
    (TypeNode("null"), InertType(InertCoreTypes.NULL)),
    (TypeNode("bool"), InertType(InertCoreTypes.BOOL)),
    (TypeNode("float"), InertType(InertCoreTypes.FLOAT)),
    (TypeNode("str"), InertType(InertCoreTypes.STR)),
    (TypeNode("int"), InertType(InertCoreTypes.INT)),
    # Inert mods correct
    (TypeNode("int", compile_const=True), InertType(InertCoreTypes.INT, const=True)),
    (TypeNode("int", nullable=True), InertType(InertCoreTypes.INT, nullable=True)),
    (TypeNode("int", group=True), None),
    (TypeNode("int", compile_const=True, nullable=True, group=True), None),
    # Exec correct
    (TypeNode("world"), ExecType(ExecCoreTypes.WORLD, False)),
    (TypeNode("world", group=True), None),
    (TypeNode("Entity"), ExecType(ExecCoreTypes.ENTITY, False)),
    (TypeNode("Entity", group=True), ExecType(ExecCoreTypes.ENTITY, True)),
    (TypeNode("entity"), None),
    (TypeNode("Player"), ExecType(ExecCoreTypes.PLAYER, False)),
    (TypeNode("Player", compile_const=True), None),
    (TypeNode("Player", nullable=True), None),
    (TypeNode("player"), None),  # Caps wrong
    # Struct correct
    (TypeNode("Pos"), StructPos.get_type()),
    (TypeNode("Pos", group=True), None),
    (TypeNode("Pos", nullable=True), None),
    (TypeNode("Pos", compile_const=True), None),
    # Fake types never work
    (TypeNode("not a real type"), None),
    (TypeNode("not a real type", group=True), None),
    (TypeNode("not a real type", nullable=True), None),
    (TypeNode("not a real type", compile_const=True), None),
    (TypeNode("not a real type", compile_const=True, nullable=True), None),
    (TypeNode("not a real type", compile_const=True, nullable=True, group=True), None),
])
def test_type_conversion(ast: TypeNode, expected_ctype: Optional[ComType]):
    if expected_ctype is None:
        with pytest.raises(ConversionError):
            convert_explicit_type(ast, _MODULE)
    else:
        assert expected_ctype == convert_explicit_type(ast, _MODULE)


def test_capitalization_help_working_player():
    with pytest.raises(ConversionError) as err_info:
        convert_explicit_type(TypeNode("player"), _MODULE)
    assert "Player" in str(err_info.value), "Correct capitalization of player missing"


def test_capitalization_help_working_int():
    with pytest.raises(ConversionError) as err_info:
        convert_explicit_type(TypeNode("Int"), _MODULE)
    assert "int" in str(err_info.value), "Correct capitalization of int missing"
