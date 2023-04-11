from typing import List

import pytest

from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.generation import convert
from mchy.errors import ConversionError
from mchy.mchy_ast.convert_parse import mchy_parse
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
    ([], r"""def echo_text(msg: str!){}""", ["msg", "echo_text", "has compile-constant type", "str!", "Consider using a global OR making runtime type"], ComLoc(1, 14, 1, 23)),
    ([], r"""if 42 {}""", ["If", "int", "bool"], ComLoc(1, 3, 1, 5)),
    ([], r"""if True {} elif 42 {}""", ["Elif", "int", "bool"], ComLoc(1, 16, 1, 18)),
    ([], r"""this""", ["this", "cannot be used outside", "function"], ComLoc(1, 0, 1, 4)),
    ([FD], r"""func(x=5, 10)""", ["Positional argument's cannot follow keyword arguments"], ComLoc(1, 10, 1, 12)),
    ([FD], r"""func(1, 2, 3, 4)""", ["only takes 3 arguments, 4 given"], ComLoc(1, 5, 1, 15)),
    ([FD], r"""func(1, 2, fake=3)""", ["fake", "not an parameter"], ComLoc(1, 11, 1, 17)),
    ([FD], r"""func(1, 2, 3, z=3)""", ["z", "already has a value"], ComLoc(1, 14, 1, 17)),
    ([FD], r"""func(1, z=3)""", ["y", "has no value"], ComLoc(1, 0, 1, 12)),
    ([], r"""world.colors.made_up_color()""", ["colors", "cannot be continued", "made_up_color"], ComLoc(1, 13, 1, 26)),
    ([], r"""world.colors.made_up_color""", ["colors", "cannot be continued", "made_up_color"], ComLoc(1, 13, 1, 26)),
    ([], r"""world.colors.red()""", ["red", "cannot invoke it as a function"], ComLoc(1, 13, 1, 16)),
    ([], r"""world.colors()""", ["colors", "cannot invoke it as a function"], ComLoc(1, 6, 1, 12)),
    ([], r"""world.colors.hex""", ["hex", "cannot invoke it as a property"], ComLoc(1, 13, 1, 16)),
    ([], r"""world.get_player""", ["get_player", "cannot invoke it as a property"], ComLoc(1, 6, 1, 16)),
    ([], r"""4.colors.red""", ["only be accessed", "executable type", "int"], ComLoc(1, 0, 1, 1)),
    ([], r"""4.colors.hex()""", ["only be accessed", "executable type", "int"], ComLoc(1, 0, 1, 1)),
    ([], r"""4.made_up_property""", ["only be accessed", "executable type", "int"], ComLoc(1, 0, 1, 1)),
    ([], r"""world.say(42)""", ["Param", "msg", "int", "str"], ComLoc(1, 10, 1, 12)),
    ([], r"""world.colors.hex(42)""", ["Param", "color_code", "int", "str"], ComLoc(1, 17, 1, 19)),
    ([], r"""print(world.pos.constant(0, 1, 2))""", ["Extra argument", "print", "Pos"], ComLoc(1, 6, 1, 33)),
    ([], r"""world.made_up_function()""", ["made_up_function", "is not defined"], ComLoc(1, 6, 1, 22)),
    ([], r"""world.made_up_function""", ["made_up_function", "is not defined"], ComLoc(1, 6, 1, 22)),
    ([], r"""made_up_var""", ["made_up_var", "is not defined"], ComLoc(1, 0, 1, 11)),
    ([], """@ticking\ndef Player foo(){}""", ["Ticking function", "world", "Player", "Consider deleting executor type"], ComLoc(2, 4, 2, 10)),
    ([], """@ticking\ndef foo(nope: int){}""", ["Ticking functions cannot have any parameters", "Consider deleting params"], ComLoc(2, 8, 2, 12)),
    ([], """@public\ndef foo(nope: int){}""", ["Published functions cannot have any parameters", "Consider deleting params"], ComLoc(2, 8, 2, 12)),
    ([], """@ticking\ndef foo() -> int {}""", ["Ticking functions cannot return anything", "Consider deleting return type"], ComLoc(2, 13, 2, 16)),
    ([], """@made_up_decorator\ndef foo(){}""", ["Unknown decorator", "made_up_decorator", "ticking"], ComLoc(1, 1, 1, 18)),
    ([], """var x: int\nvar x: int""", ["x", "already defined in current scope", "var x: int"], ComLoc(2, 4, 2, 5)),
    ([], """var x: int = 1\nvar x: int = 2""", ["x", "already defined in current scope", "var x: int", "did you mean `x = 2`"], ComLoc(2, 4, 2, 5)),
    ([], """var x: int\nvar x: int = 1""", ["x", "already defined in current scope", "var x: int"], ComLoc(2, 4, 2, 5)),
    ([], """var x: int = 1\nvar x: int""", ["x", "already defined in current scope", "var x: int"], ComLoc(2, 4, 2, 5)),
    ([], """let x: int = 1\nvar x: int""", ["x", "already defined in current scope", "let x: int"], ComLoc(2, 4, 2, 5)),
    ([], """var x: int\nvar x: str""", ["x", "already defined in current scope", "var x: int"], ComLoc(2, 4, 2, 5)),
    ([], r"""var x: int = 'foo'""", ["Cannot assign expression", "str!", "int"], ComLoc(1, 13, 1, 18)),
    ([FD], r"""var x: str! = func(1, 2, 3)""", ["Cannot assign expression", "int", "str!"], ComLoc(1, 14, 1, 27)),
    ([FD], r"""var x: int! = func(1, 2, 3)""", ["Compile-constants", "constant type", "int"], ComLoc(1, 14, 1, 27)),
    ([], """var x: int! = 5\nx = 10""", ["compile-constant", "cannot be assigned to", "int"], ComLoc(2, 0, 2, 6)),
    ([], """let x: int = 5\nx = 10""", ["read-only", "cannot be assigned to", "int"], ComLoc(2, 0, 2, 6)),
    ([], """var x: Color = world.colors.red\nx = world.colors.blue""", ["struct variables", "read-only", "cannot be assigned to", "Color"], ComLoc(2, 0, 2, 21)),
    ([], r"""var x: pop""", ["type", "pop", "not known"], ComLoc(1, 7, 1, 10)),
    ([], r"""var x: Int""", ["type", "Int", "not known", "did you mean", "int"], ComLoc(1, 7, 1, 10)),
    ([], r"""var x: Pos!""", ["Struct", "compile-constant", "`Pos!` -> `Pos`"], ComLoc(1, 7, 1, 11)),
    ([], r"""var x: Pos?""", ["Struct", "nullable", "`Pos?` -> `Pos`"], ComLoc(1, 7, 1, 11)),
    ([], r"""var x: Group[Pos]""", ["Struct", "grouped", "`Group[Pos]` -> `Pos`"], ComLoc(1, 7, 1, 17)),
    ([], r"""var x: Player!""", ["Executable types", "compile-constant", "Player! -> Player"], ComLoc(1, 7, 1, 14)),
    ([], r"""var x: Player?""", ["Executable types", "nullable", "Player? -> Player"], ComLoc(1, 7, 1, 14)),
    ([], r"""var x: Group[int]""", ["group", "inert", "Group[int] -> int"], ComLoc(1, 7, 1, 17)),
    ([], r"""var x: null?""", ["nullable", "`null?` -> `null`"], ComLoc(1, 7, 1, 12)),
    ([FD], r"""def func(new_param: int) -> int {}""", ["func", "already defined"], ComLoc(1, 0, 1, 31)),
])
def test_conv_error_expected(test_code: str, expected_msgs: List[str], err_loc: ComLoc, setup_code: List[str]):
    # Fix line numbers
    setup_code_str = ("\n".join(setup_code)+"\n").lstrip("\n")
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
        f"Location mismatch for code {repr(test_code)},\n" +
        f"  > which as anticipated raised the error: \"{str(err_info.value)}\"\n" +
        f"  > Location diff: " + loc_diff(err_info.value.loc, err_loc)
    )
