
from mchy.errors import ConversionError
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_give():
    code = """
    var all_players: Group[Player] = world.get_players().find()

    all_players.give("minecraft:apple", 2)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"give @a.* minecraft:apple(\{.*\})? 2"
    ), "A give command providing 2 apples cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_give_negative_count():
    code = """
    var all_players: Group[Player] = world.get_players().find()

    all_players.give("minecraft:apple", -16)
    """
    with pytest.raises(ConversionError) as err_info:
        ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert err_info.match(r".*[Gg]ive.*cannot be less than 1"), f"Error does not match expectation, Error info: {err_info}"
