from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


# TODO: add test using struct like  once string escaping working


def test_simple_summon():
    code = """
    var player: Group[Player] = world.get_players().find()

    var zombie: Entity = summon(player.pos.get(), "minecraft:zombie")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""^execute.*at.*run summon minecraft:zombie ~0? ~0? ~0? \{Tags:\[\"[^\"]+-mchy_glob-var_[0-9]+\"\]\}"""
    ), "A summon command creating a zombie with a valid tag cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_data_summon():
    code = """
    var player: Group[Player] = world.get_players().find()

    var zombie: Entity = summon(player.pos.get(), "minecraft:zombie", "{CustomName:'{\\"text\\":\\"Zed2\\"}'}")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""^execute.*at.*run summon minecraft:zombie ~0? ~0? ~0? \{CustomName:'{"text":"Zed2"}',Tags:\[\"[^\"]+-mchy_glob-var_[0-9]+\"\]\}"""
    ), "A summon command creating a zombie with a valid tag cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_pre_tagged_summon():
    code = """
    var player: Group[Player] = world.get_players().find()

    var zombie: Entity = summon(player.pos.get(), "minecraft:zombie", "{Tags:[\\"greg\\"]}")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"""^execute.*at.*run summon minecraft:zombie ~0? ~0? ~0? \{Tags:\[\"greg\", *\"[^\"]+-mchy_glob-var_[0-9]+\"\]\}"""
    ), "A summon command creating a zombie with a valid tag cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
