import re
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_gte_var():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (x1 <= x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""execute store result score var_.* .*mchy_glob run execute if score var_x2 .*mchy_glob >= var_x1 .*mchy_glob"""
    ), f"A command checking x2 >= x1 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_gt_var():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (x1 < x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""execute store result score var_.* .*mchy_glob run execute if score var_x2 .*mchy_glob > var_x1 .*mchy_glob"""
    ), f"A command checking x2 > x1 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_gte_rhs_const():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (x1 <= 21)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r""".*execute if score var_x1 .*mchy_glob matches ..21"""
    ), f"A command checking x1 <= 21 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_gt_rhs_const():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (x1 < 21)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r""".*execute if score var_x1 .*mchy_glob matches ..20"""
    ), f"A command checking x1 < 21 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_gte_lhs_const():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (13 <= x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r""".*execute if score var_x2 .*mchy_glob matches 13.."""
    ), f"A command checking 13 <= x2 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_gt_lhs_const():
    code = """
    var x1: int = 14
    var x2: int = 19

    var y1: bool = (13 < x2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r""".*execute if score var_x2 .*mchy_glob matches 14.."""
    ), f"A command checking 13 < x2 cannot be found; raw file:\n"+vir_dp.load_master_file.get_file_data()
