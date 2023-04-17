import re
from mchy.virtual.vir_dirs import VirMCHYFile
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_public_funcs():
    code = """
    @public
    def foo(){}

    @public
    def bar() -> int {return 42}
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    # file validation
    assert vir_dp.public_funcs_accessor_fld.get_child_with_name("foo.mcfunction") is not None, "public didn't result in public function foo?"
    assert (bar_file := vir_dp.public_funcs_accessor_fld.get_child_with_name("bar.mcfunction")) is not None, "public didn't result in public function bar?"
    assert isinstance(bar_file, VirMCHYFile), "bar unexpectedly not a mchy file? (even though it has extension `.mcfunction`???)"

    # bar includes return print
    assert (
        match := re.search(r"scoreboard players operation (var_[0-9]+) .* = return .*mchy_func.*bar.*", bar_file.get_file_data())
    ), "Cannot find line setting pseudo var to function return, raw file:\n"+bar_file.get_file_data()

    assert any_line_matches(
        bar_file, f"""tellraw @a.*score.*{match.group(1)}"""
    ), f"A command printing the pseudo var ({match.group(1)}), cannot be found; raw file:\n"+bar_file.get_file_data()
