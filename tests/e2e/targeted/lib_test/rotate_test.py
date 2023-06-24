from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_rotate_face():
    code = """
    let ply: Player = world.get_player().find()
    let target: Entity = ply.get_entity(sort="nearest").in_radius(min=1).find()

    ply.rotate.face(target.pos.get())
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r".*tp @s ~ ~ ~ facing entity.*"
    ), "A tp-entity-facing command cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
