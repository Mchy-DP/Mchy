from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_particle():
    code = """
    var cog: Entity = world.get_entity("nearest").of_name("cog").find()

    world.particle(cog.pos.get(), "minecraft:flame", 0.1, 0.1, 0.1, 0.15, 100, True)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r".*particle minecraft:flame.*0.1 0.1 0.1 0.15 100 force"
    ), "A particle command cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
