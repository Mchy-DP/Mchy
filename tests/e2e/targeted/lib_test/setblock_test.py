from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_setblock_and_pos_ops():
    code = """
    var random_player: Player = world.get_player("random").find()
    var nearest_creeper: Entity = random_player.get_entity().of_type("minecraft:creeper").find()

    var const_pos: Pos = world.pos.constant(x=-9, y=78, z=-44)
    var creeper_pos: Pos = nearest_creeper.pos.get()
    var creeper_pos_y75: Pos = world.pos.set_coord(creeper_pos, force_y=80)

    world.setblock(const_pos, "minecraft:diamond_block")
    world.setblock(creeper_pos_y75, "minecraft:emerald_block")

    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^setblock.*-9 78 -44.*minecraft:diamond_block"
    ), "A setblock command targeting -9 78 -44 and setting a diamond block cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"^execute.*@e[^\]]*tag=.*run setblock.*~(0(\.0)?)? 80(\.0)? ~(0(\.0)?)?.*minecraft:emerald_block"
    ), "A setblock command executing as tagged entity targeting ~ 80 ~ and setting a emerald block cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
