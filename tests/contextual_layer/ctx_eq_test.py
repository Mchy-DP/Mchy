
import pytest
from mchy.common.com_loc import ComLoc

from mchy.contextual.struct import *


@pytest.mark.parametrize("result, left, right", [
    (True, CtxExprLitBool(False, src_loc=ComLoc()), CtxExprLitBool(False, src_loc=ComLoc())),
    (False, CtxExprLitBool(True, src_loc=ComLoc()), CtxExprLitBool(False, src_loc=ComLoc())),
])
def test_eq(result: bool, left, right):
    assert (left == right) == result
