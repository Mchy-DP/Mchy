
from typing import Collection, Optional, Sequence
from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.properties import IProp
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import *
from mchy.contextual.struct.module import CtxModule
from mchy.errors import ConversionError
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


class LiterallyJustReturnSixWithPointlessParam(IFunc):

    def get_namespace(self) -> 'Namespace':
        return _TESTING_NS

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get6"

    def get_params(self) -> Sequence[IParam]:
        return [IParam("pointless", InertType(InertCoreTypes.INT), None)]

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

_TST_GET4 = _TESTING_MODULE.get_property_oerr(ExecType(ExecCoreTypes.WORLD, False), "get4")
_TST_GET5 = _TESTING_MODULE.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "get5")
_TST_GET6 = _TESTING_MODULE.get_function_oerr(ExecType(ExecCoreTypes.WORLD, False), "get6")
_MOCK_WORLD_EXECUTOR = CtxTTypeNode(ExecType(ExecCoreTypes.WORLD, False))

_LOC = ComLoc()


@pytest.mark.parametrize("expr, expected_type", [
    (CtxExprPropertyAccess(_MOCK_WORLD_EXECUTOR, _TST_GET4, src_loc=_LOC), InertType(InertCoreTypes.INT, False, False)),
    (CtxExprFuncCall(_MOCK_WORLD_EXECUTOR, _TST_GET5, [], src_loc=_LOC), InertType(InertCoreTypes.INT, False, False)),
    (CtxExprFuncCall(_MOCK_WORLD_EXECUTOR, _TST_GET6, [
        CtxExprParamVal(_TST_GET6.get_param("pointless"), CtxExprLitInt(42, src_loc=_LOC), src_loc=_LOC)  # type: ignore  # The type is noted as being nullable but it won't be
        ], src_loc=_LOC), InertType(InertCoreTypes.INT, False, False)),
])
def test_expr_type_correct(expr: CtxExprNode, expected_type: Optional[ComType]):
    if expected_type is None:
        with pytest.raises(ConversionError):
            expr.get_type()
    else:
        assert expr.get_type() == expected_type
