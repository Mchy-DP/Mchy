from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest

_ERR_PREFIX = "A selector matching expected response from sub-selector"


def test_selector_from_position(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().from_position(420, 421, 422).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag @a\[.*x=420,.*y=421,.*z=422.*\] add "
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_in_radius(request: pytest.FixtureRequest):
    code = """
    var thing1: Group[Player] = world.get_players().in_radius(5, 10).find()
    var thing2: Group[Player] = world.get_players().in_radius(null, 13).find()
    var thing3: Group[Player] = world.get_players().in_radius(7, null).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag @a\[.*distance=5\.\.10.*\] add "
    ), f"{_ERR_PREFIX} 1 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag @a\[.*distance=\.\.13.*\] add "
    ), f"{_ERR_PREFIX} 2 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag @a\[.*distance=7\.\..*\] add "
    ), f"{_ERR_PREFIX} 3 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_in_volume(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().in_volume(7, 11, 19).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag @a\[.*dx=7,.*dy=11,.*dz=19.*\] add "
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_in_team_specific(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().in_team("fred").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*team=fred.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_in_team_any(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().in_team(null).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*team=!.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_not_in_team(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().not_in_team("fred").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*team=!fred.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_with_no_team(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().with_no_team().find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*team=.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_with_tag(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().with_tag("foo").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*tag=foo.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_without_tag(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().without_tag("foo").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*tag=!foo.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_score(request: pytest.FixtureRequest):
    code = """
    var thing1: Group[Player] = world.get_players().with_score("obj_foo", 5, 10).find()
    var thing2: Group[Player] = world.get_players().with_score("obj_foo", null, 13).find()
    var thing3: Group[Player] = world.get_players().with_score("obj_foo", 7, null).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*scores={obj_foo=5..10}.*\] add '
    ), f"{_ERR_PREFIX} 1 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*scores={obj_foo=..13}.*\] add '
    ), f"{_ERR_PREFIX} 2 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*scores={obj_foo=7..}.*\] add '
    ), f"{_ERR_PREFIX} 3 of `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_of_type(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Entity] = world.get_entities().of_type("minecraft:pig").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @e\[.*type=minecraft:pig.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_of_name(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().of_name("foo").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*name="foo".*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_passing_predicate(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().passing_predicate("ns:is_sneaking").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*predicate=ns:is_sneaking.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_failing_predicate(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().failing_predicate("ns:is_sneaking").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*predicate=!ns:is_sneaking.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_with_vert_rot(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().with_vert_rot(45, 135).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*x_rotation=45..135.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_with_hrz_rot(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().with_hrz_rot(-45, 45).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*y_rotation=-45..45.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_matching_nbt(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().matching_nbt("{NoAI:1b}").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*nbt={NoAI:1b}.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_not_matching_nbt(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().not_matching_nbt("{NoAI:1b}").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*nbt=!{NoAI:1b}.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_with_level(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().with_level(5, 10).find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*level=5..10.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_in_gamemode(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().in_gamemode("creative").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*gamemode=creative.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_not_in_gamemode(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().not_in_gamemode("creative").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*gamemode=!creative.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_advancement_matches(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().advancement_matches("story/mine_stone=true").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*advancements={story/mine_stone=true}.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_selector_advancement_matches_multi(request: pytest.FixtureRequest):
    code = """
    var thing: Group[Player] = world.get_players().advancement_matches("story/mine_stone=true").advancement_matches("story/smelt_iron=true").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r'^tag @a\[.*advancements={story/mine_stone=true,story/smelt_iron=true}.*\] add '
    ), f"{_ERR_PREFIX} `{request.node.originalname[len('test_selector_'):]}` cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
