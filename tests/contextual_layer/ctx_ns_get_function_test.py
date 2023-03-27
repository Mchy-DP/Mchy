from typing import Collection, Sequence
from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.properties import IProp
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import *
from mchy.contextual.struct.module import CtxModule
from tests.contextual_layer.helpers import CtxTTypeNode
from tests.helpers.tst_ns import ROOT_TESTING_NAMESPACE

import pytest


_TESTING_NS = Namespace("test", ROOT_TESTING_NAMESPACE)


class LiterallyJustReturnFive(IFunc):

    def get_namespace(self) -> 'Namespace':
        return _TESTING_NS

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get5"

    def get_params(self) -> Sequence[IParam]:
        return []

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)


class LiterallyJustReturnFifty(IFunc):

    def get_namespace(self) -> 'Namespace':
        return _TESTING_NS

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, False)

    def get_name(self) -> str:
        return "get50"

    def get_params(self) -> Sequence[IParam]:
        return []

    def get_return_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)


class LiterallyJustTheValueFour(IProp):

    def get_namespace(self) -> 'Namespace':
        return _TESTING_NS

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get4"

    def get_prop_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)


_TESTING_MODULE = CtxModule(Config())
_TESTING_MODULE.import_ns(_TESTING_NS)


@pytest.mark.parametrize("executor, name, expect_exists", [
    (ExecType(ExecCoreTypes.WORLD, False), "get5", True),
    (ExecType(ExecCoreTypes.ENTITY, False), "get5", True),
    (ExecType(ExecCoreTypes.ENTITY, True), "get5", True),
    (ExecType(ExecCoreTypes.PLAYER, False), "get5", True),
    (ExecType(ExecCoreTypes.PLAYER, True), "get5", True),

    (ExecType(ExecCoreTypes.WORLD, False), "get50", False),
    (ExecType(ExecCoreTypes.ENTITY, False), "get50", True),
    (ExecType(ExecCoreTypes.ENTITY, True), "get50", True),  # Will operation on each entity individually in the group
    (ExecType(ExecCoreTypes.PLAYER, False), "get50", True),
    (ExecType(ExecCoreTypes.PLAYER, True), "get50", True),  # Will operation on each entity individually in the group
])
def test_get_func(executor: ExecType, name: str, expect_exists: bool):
    if expect_exists:
        assert _TESTING_MODULE.get_function(executor, name) is not None, f"Function of name `{name}` unexpectedly not found upon executor `{executor.render()}`"
    else:
        assert _TESTING_MODULE.get_function(executor, name) is None, f"Function of name `{name}` unexpectedly found upon executor `{executor.render()}`"
    assert _TESTING_MODULE.func_defined(executor, name) == expect_exists, "Inconsistent behavior between get function and func defined"
