from typing import List, Union
import pytest
from mchy.common.com_logger import ComLogger
from mchy.common.config import Config
from mchy.errors import MchySyntaxError

from mchy.mchy_ast.convert_parse import mchy_parse


_TEST_CONFIG = Config(verbosity=Config.Verbosity.VV, logger=ComLogger(std_out_level=ComLogger.Level.VeryVerbose, unique_name=f"PYTEST-{__name__}"))


@pytest.mark.parametrize("code, error_message_match", [
    ("", ["Empty file"]),
    ("\n", ["Empty file"]),
    ("\n\n", ["Empty file"]),
    ("fo`o", ["Invalid char", "`"]),
    ("var foo = 1", ["Missing type annotation", "foo"]),
    ("var g: int = 0\nvar foo = 1", ["Missing type annotation", "foo"]),
    ("var foo = 1\nvar g: int = 0", ["Missing type annotation", "foo"]),
    ("var bar: = 1", ["Missing type", "bar"]),
    ("var h: Group = 1", ["Incomplete type", "["]),
    ("var h: Group[world] = 1", ["Cannot have groups of world"]),
    ("var h: int =", ["Cannot assign to nothing"]),
    ("int v", ["No valid option", "int v", "var v: int"]),
    ("h =", ["Cannot assign to nothing"]),
    ("var h: int =\n", ["Cannot assign to nothing"]),
    ("h =\n", ["Cannot assign to nothing"]),
    ("var h: int =}", ["Cannot assign to nothing"]),
    ("h =}", ["Cannot assign to nothing"]),
    ('if x > 5:\n    print("hello!")\n', ["{", "not indentation"]),
    ('if x > 5{}elif x < 2:\n    print("hello!")\n', ["{", "not indentation"]),
    ('if x > 5{}elif x < 2{}else:\n    print("hello!")\n', ["{", "not indentation"]),
    ("def func_name(){if (true)}", ["Missing", "body", "{}"]),
    ("def func_name(){if (true){} elif (true)}", ["Missing", "body", "{}"]),
    ("def func_name(){if (true){} elif (true){} else}", ["Missing", "body", "{}"]),
    ('def f(bar){}', ["Missing type annotation", "param", "bar"]),
    ('def foo():\n    print("hi")\n', ["{", "not indentation"]),
    ('def foo(){\n    return\n}', ["Expected expression", "got '\\n'", "return null"]),
    ('def foo(){\n    return}', ["Expected expression", "got '}'", "return null"]),
    ('def foo(){\n    return', ["Expected expression", "got '<EOF>'", "return null"]),
    ('def foo(){\n    return ->', ["Expected expression", "got '->'"]),
    ('def foo(p1bar:){}', ["Missing type", "param", "p1bar"]),
    ('def foo(p1bar:,p2){}', ["Missing type", "param", "p1bar"]),
    ('function foo(p1: int)', ["No valid option", "function foo", "def foo"]),
    ('def foo(int p1){}', ["Invalid type annotation", "p1: int"]),
    ('var x: int = for while', ["keyword", "for"]),
    ('var x: int = for 3', ["keyword", "for"]),
    ('var x: int = -> while', ["expected expression"]),
    ('var x: int = -> 3', ["expected expression"]),
    ('x.y = 4', ["Cannot assign to non-variable"]),
    ('(x)[2] = 1', ["Cannot use '[' in this context"]),
    ('x[2] = 1', ["Cannot use '[' in this context"]),
    ('var foo: grup[Player]', ["Invalid type", "grup[", "foo", "Group["]),
    ('def foo(){var foo: grup[Player]}', ["Invalid type", "grup[", "foo", "Group["]),
    ('def foo() -> int {\nreturn 42\n}s', ["s", "\\n"]),
    ('if true {', ["File ended unexpectedly", "closing scope", "}"]),
    ('{', ["Cannot open code block"]),
    ('{}', ["Cannot open code block"]),
])
def test_parse_raises(code: str, error_message_match: Union[str, List[str]]):
    if isinstance(error_message_match, str):
        error_message_match = [error_message_match]
    with pytest.raises(MchySyntaxError) as exc_info:
        mchy_parse(code, _TEST_CONFIG)
    for match in error_message_match:
        assert match in str(exc_info.value), f"The string `{match}` could not be found in the exception {repr(exc_info.value)}"
