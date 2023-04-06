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
    ), "A tp command cannot be found cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_constant_tp_with_ints():
    code = """
    var player: Player = world.get_player().find()
    player.tp(world.pos.constant(10, 75, 10))
    """

    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"tp @a.*var_player.* 10 75 10"
    ), "A int-float tp command cannot be found cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_constant_tp_with_floats():
    code = """
    var player: Player = world.get_player().find()
    player.tp(world.pos.constant(10.3, 74.5, 10.3))
    """

    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"tp @a.*var_player.* 10.3 74.5 10.3"
    ), "A tp const-float command cannot be found cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_directed_tp_with_floats():
    code = """
    var player: Player = world.get_player().find()
    player.tp(player.pos.get_directed(0.01, 0.01, 0.5))
    """

    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute at @a.*var_player.* run tp @a.*var_player.* \^0.01 \^0.01 \^0.5"
    ), "A directed tp command cannot be found cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_reletive_tp_with_floats():
    code = """
    var player: Player = world.get_player().find()
    player.tp(player.pos.get(-0.01, 10.2, -0.01))
    """

    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute at @a.*var_player.* run tp @a.*var_player.* ~-0.01 ~10.2 ~-0.01"
    ), "A relative tp command cannot be found cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
