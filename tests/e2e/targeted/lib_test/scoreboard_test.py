
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_scoreboard_name_conf():
    code = """
    world.scoreboard.add_obj("fake101")
    world.scoreboard.conf.json_name("fake101",
        world.colors.hex("#ff0000"), "F",
        world.colors.hex("#ff8800"), "a",
        world.colors.hex("#88ff00"), "k",
        world.colors.hex("#00ff00"), "e",
        world.colors.hex("#00ff88"), "1",
        world.colors.hex("#0088ff"), "0",
        world.colors.hex("#0000ff"), "1",
        world.colors.hex("#8800ff"), "!",
        world.colors.hex("#ff0088"), "?"
    )
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard objectives add fake101 dummy"
    ), "The command 'scoreboard objectives add fake101 dummy' cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard objectives modify fake101 displayname.*#ff0000.*F.*#ff8800.*a.*#88ff00.*k.*#ff0088.*\?"
    ), "A command starting 'scoreboard objectives modify fake101 displayname' followed by json comps cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_scoreboard_exec_ops():
    code = """
    # Setup
    let OBJ: str! = "fake202"
    world.scoreboard.add_obj(OBJ)
    world.scoreboard.conf.display.sidebar(OBJ)
    let player: Player = world.get_player("nearest").find()

    # Test
    var score: int = player.scoreboard.obj(OBJ).get()
    score = score + 3
    player.scoreboard.obj(OBJ).set(score)
    player.scoreboard.obj(OBJ).add(5)
    player.scoreboard.obj(OBJ).sub(9)

    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r".*scoreboard players get.*fake202"
    ), "cannot find command matching `scoreboard players get.*fake202`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r".*fake202.*= var_score.*mchy_glob"
    ), "cannot find command matching `.*fake202.*= var_score.*mchy_glob`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players add.*fake202 5"
    ), "cannot find command matching `scoreboard players add.*fake202 5`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players remove.*fake202 9"
    ), "cannot find command matching `scoreboard players remove.*fake202 9`, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_scoreboard_fake_player_ops():
    code = """
    # Setup
    let OBJ: str! = "fake202"
    let PLY: str! = "fakePL"
    world.scoreboard.add_obj(OBJ)
    world.scoreboard.conf.display.sidebar(OBJ)

    # Test
    var score: int = world.scoreboard.obj(OBJ).player(PLY).get()
    score = score + 3
    world.scoreboard.obj(OBJ).player(PLY).set(score)
    world.scoreboard.obj(OBJ).player(PLY).add(5)
    world.scoreboard.obj(OBJ).player(PLY).sub(9)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r".*scoreboard players get fakePL fake202"
    ), "cannot find command matching `scoreboard players get.*fake202`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players operation fakePL fake202 = var_score .*mchy_glob"
    ), "cannot find command matching `scoreboard players operation fakePL fake202 = var_score .*mchy_glob`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players add fakePL fake202 5"
    ), "cannot find command matching `scoreboard players add fakePL fake202 5`, raw file:\n"+vir_dp.load_master_file.get_file_data()

    assert any_line_matches(
        vir_dp.load_master_file, r"scoreboard players remove fakePL fake202 9"
    ), "cannot find command matching `scoreboard players remove fakePL fake202 9`, raw file:\n"+vir_dp.load_master_file.get_file_data()
