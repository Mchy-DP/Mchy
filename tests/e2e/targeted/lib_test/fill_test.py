
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_effect():
    code = """
    var greg: Entity = world.get_entity("nearest").of_name("greg").find()

    world.fill(greg.pos.get(-3,10,-3), greg.pos.get(3,10,3), "minecraft:blue_stained_glass", keep_existing=True)
    world.area_replace(greg.pos.get(-2,10,-2), greg.pos.get(2,10,2), "minecraft:blue_stained_glass", "minecraft:light_blue_stained_glass")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r".*fill.*~-3 ~10 ~-3 ~3 ~10 ~3.*minecraft:blue_stained_glass.*keep"
    ), "A fill command placing radius 3 blue glass cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r".*fill.*~-2 ~10 ~-2 ~2 ~10 ~2.*minecraft:light_blue_stained_glass.*replace.*minecraft:blue_stained_glass"
    ), "A fill command replacing in radius 2 blue glass with light blue glass cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
