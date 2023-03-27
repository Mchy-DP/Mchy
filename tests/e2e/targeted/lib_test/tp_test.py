from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_tp():
    code = """
    var cog: Entity = world.get_entity("nearest").of_name("cog").find()
    var player: Player = world.get_player().find()


    cog.tp(player.pos.get())
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute at @a.*var_player.* run tp @e.*var_cog.* ~[^\~]*~[^\~]*~[^\~]*"
    ), "A setblock command targeting -9 78 -44 and setting a diamond block cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
