import re
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_simple_summon():
    code = """
    var x1: int? = 5
    var x2: int? = null

    var y1: int = x1 ?? 10
    var y2: int = x2 ?? 12

    print(y1, y2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""scoreboard players set var_x1.*5"""
    ), "A command setting x1 to 5 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"""data modify storage.*var_x2.is_null.*"""
    ), "A command setting x2 to null cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    # Y1 matches
    assert (
        match := re.search(r"scoreboard players operation (var_.*) .*mchy_glob = var_x1 .*mchy_glob", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to var x1, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f""".*scoreboard players set {match.group(1)} .*mchy_glob 10"""
    ), f"A command setting the same pseudo var ({match.group(1)}) to 10 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f""".*scoreboard players operation var_y1 .*mchy_glob = {match.group(1)} .*mchy_glob"""
    ), f"A command setting y1 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    # Y2 matches
    assert (
        match := re.search(r"execute store result score (var_.*) .*mchy_glob run data get storage .*mchy_glob.var_x2.value", vir_dp.load_master_file.get_file_data())
    ), "Cannot find line setting pseudo var to var x2, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f""".*scoreboard players set {match.group(1)} .*mchy_glob 12"""
    ), f"A command setting the same pseudo var ({match.group(1)}) to 12 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, f""".*scoreboard players operation var_y2 .*mchy_glob = {match.group(1)} .*mchy_glob"""
    ), f"A command setting y2 to the same pseudo var ({match.group(1)}) cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
