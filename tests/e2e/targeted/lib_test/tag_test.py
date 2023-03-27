from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_add_tag_cmd():
    code = """
    var cog: Group[Entity] = world.get_entities().of_name("cog").find()

    cog.tag_add("good_tag")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"tag.*var_cog.*add good_tag"
    ), "A tag command adding good_tag to var_cog tagged entities cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_remove_tag_cmd():
    code = """
    var cog: Group[Entity] = world.get_entities().of_name("cog").find()

    cog.tag_remove("good_tag")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"tag.*var_cog.*remove good_tag"
    ), "A tag command removing good_tag to var_cog tagged entities cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_count_tag_cmd():
    code = """
    var cog: Group[Entity] = world.get_entities().of_name("cog").find()

    print(cog.tag_count())
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute.*store.*run.*tag.*var_cog.*list"
    ), "A command counting entity tags cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
