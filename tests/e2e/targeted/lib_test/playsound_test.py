from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_playsound():
    code = """
    var player: Player = world.get_player().find()

    player.play_sound(player.pos.get(), "minecraft:block.anvil.use")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^execute.*at @a.*var_player.*run playsound minecraft:block.anvil.use master @a.*var_player.*~[^\~]*~[^\~]*~[^\~]*1.0 1.0 0.0"
    ), "A playsound command cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
