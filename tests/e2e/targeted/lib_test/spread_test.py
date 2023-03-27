from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_spreadplayer_test():
    code = """
    var cog: Group[Entity] = world.get_entities().of_name("cog").find()
    var player: Player = world.get_player().find()

    cog.spread(player.pos.get(), 5)
    """  # This code randomly distributes all loaded entities called cog within 5 blocks of a arbitrary player
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute at @a.*var_player.*run spreadplayers ~[^\~]* ~[^\~]* 0(.0)? 5(.0)? false @e.*var_cog.*"
    ), "A spreadplayers command cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
