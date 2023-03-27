from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_kill_cmd():
    code = """
    var cog: Group[Entity] = world.get_entities().of_name("cog").find()

    cog.kill()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"kill.*var_cog.*"
    ), "A kill command targeting something tagged with a tag containing var_cog cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
