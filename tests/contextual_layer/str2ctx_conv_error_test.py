from typing import List

import pytest

from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.generation import convert
from mchy.errors import ConversionError
from mchy.mchy_ast.mchy_parse import mchy_parse
from mchy.mchy_ast.nodes import Root
from tests.helpers.diff_locs import loc_diff

_TEST_CONFIG = Config()

FD = r"""
def func(x: int, y: int, z: int = null) -> int{
    return 42
}
"""


@pytest.mark.parametrize("setup_code, test_code, expected_msgs, err_loc", [
    ([], r"""return 5""", ["Return", "outside", "function"], ComLoc(1, 0, 1, 8)),
    ([], r"""def int func(){}""", ["executor type", "cannot be inert", "int"], ComLoc(1, 4, 1, 7)),
    ([], r"""def func_name(param_a: int, param_a: str){}""", ["Duplicate argument", "param_a", "func_name"], ComLoc(1, 0, 1, 43)),
    ([], r"""if 42 {}""", ["If", "int", "bool"], ComLoc(1, 3, 1, 5)),
    ([], r"""if True {} elif 42 {}""", ["Elif", "int", "bool"], ComLoc(1, 16, 1, 18)),
    ([], r"""this""", ["this", "cannot be used outside", "function"], ComLoc(1, 0, 1, 4)),
    ([FD], r"""func(x=5, 10)""", ["Positional argument's cannot follow keyword arguments"], ComLoc(1, 10, 1, 12)),
    ([FD], r"""func(1, 2, 3, 4)""", ["only takes 3 arguments, 4 given"], ComLoc(1, 5, 1, 15)),
])
def test_conv_error_expected(test_code: str, expected_msgs: List[str], err_loc: ComLoc, setup_code: List[str]):
    # Fix line numbers
    setup_code_str = "\n".join(setup_code)+"\n"
    line_offset = setup_code_str.count("\n")
    err_loc = err_loc.with_line(err_loc.line_start_int + line_offset).with_line_end(err_loc.line_end_int + line_offset)
    # Get AST
    root_node: Root = mchy_parse(setup_code_str+test_code, _TEST_CONFIG)
    # Attempt to get CTXModule capturing err
    with pytest.raises(ConversionError) as err_info:
        convert(root_node, _TEST_CONFIG)

    for expected_msg in expected_msgs:
        assert expected_msg in str(err_info.value), f"The string `{expected_msg}` is not in the error message `{repr(err_info.value)}`"

    assert err_info.value.loc == err_loc, (
        f"Location mismatch for code {repr(test_code)}, diff: " + loc_diff(err_info.value.loc, err_loc)
    )
