from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_effect():
    code = """
    var random_player: Player = world.get_player("random").find()

    random_player.effect_clear("speed")
    random_player.effect_add("speed", 42, 73, False)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^effect clear.*speed"
    ), "A effect command clearing speed cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"^effect give.*speed.*42.*73"
    ), "A effect command giving speed cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
