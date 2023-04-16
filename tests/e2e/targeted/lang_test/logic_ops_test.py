import re
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


# ----- NOT -----

def test_not():
    code = """
    var x1: bool = True

    print(not x1)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .* 1", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 1, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"""execute if score var_x1 .* matches 1.. run scoreboard players set {match.group(1)} .* 0"""
    ), f"A command setting the same pseudo var ({match.group(1)}) to 0, if x is true, cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


# ----- AND -----

def test_and_var():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = x1 and x2
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .* 0", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 0, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"""execute if score var_x2.*matches 1.. if score var_x1.*matches 1.. run scoreboard players set {match.group(1)}.*1"""
    ), f"A command setting the same pseudo var ({match.group(1)}) to 1, if x1 and x2 are true, cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_and_rhs_true():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (x1 and true)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation.*= var_x1 .*-mchy_glob"
    ), "A command assigning something to var_x1 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation var_y1 .*-mchy_glob =.*"
    ), "A command assigning var_y1 to something cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_and_lhs_true():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (true and x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation.*= var_x2 .*-mchy_glob"
    ), "A command assigning something to var_x2 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation var_y1 .*-mchy_glob =.*"
    ), "A command assigning var_y1 to something cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_and_rhs_false():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (x1 and false)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .*-mchy_glob 0", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 0, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"scoreboard players operation var_y1 .*-mchy_glob = {match.group(1)} .*-mchy_glob"
    ), f"A command assigning var_y1 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_and_lhs_false():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (false and x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .*-mchy_glob 0", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 0, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"scoreboard players operation var_y1 .*-mchy_glob = {match.group(1)} .*-mchy_glob"
    ), f"A command assigning var_y1 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


# ----- OR -----

def test_or_var():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (x1 or x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .* 1", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 1, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"""execute if score var_x2.*matches ..0 if score var_x1.*matches ..0 run scoreboard players set {match.group(1)}.*0"""
    ), f"A command setting the same pseudo var ({match.group(1)}) to 0, if x1 and x2 are false, cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_or_rhs_false():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (x1 or false)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation.*= var_x1 .*-mchy_glob"
    ), "A command assigning something to var_x1 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation var_y1 .*-mchy_glob =.*"
    ), "A command assigning var_y1 to something cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_or_lhs_false():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (false or x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation.*= var_x2 .*-mchy_glob"
    ), "A command assigning something to var_x2 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation var_y1 .*-mchy_glob =.*"
    ), "A command assigning var_y1 to something cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_or_rhs_true():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (x1 or true)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .*-mchy_glob 1", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 1, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"scoreboard players operation var_y1 .*-mchy_glob = {match.group(1)} .*-mchy_glob"
    ), f"A command assigning var_y1 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_or_lhs_true():
    code = """
    var x1: bool = True
    var x2: bool = True

    var y1: bool = (true or x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert (
        match := re.search(r"scoreboard players set (var_[0-9]+) .*-mchy_glob 1", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to 1, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f"scoreboard players operation var_y1 .*-mchy_glob = {match.group(1)} .*-mchy_glob"
    ), f"A command assigning var_y1 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
