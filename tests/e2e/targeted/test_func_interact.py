from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_entity_calling_func():
    code = """
    var player: Player = world.get_player("nearest").find()
    var ent: Entity = player.get_entity("nearest").with_tag("mn").find()
    ent.say("we are one")

    def Entity say_hi(){
        this.say("Hi!")
        print("My score is: ", world.colors.light_purple, this.scoreboard.obj("fake202").get())
    }
    ent.say_hi()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute as .*limit=1.* run function [^: ]+:generated/internal_root/mchy_func/say_hi_entity/s1/run"
    ), "A command calling the function cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_entity_cast_down_calling_func():
    code = """
    var player: Player = world.get_player("nearest").find()
    var ents: Group[Entity] = player.get_entities().with_tag("mn").find()
    ents.say("we are all")

    def Entity say_hi(){
        this.say("Hi!")
        print("My score is: ", world.colors.light_purple, this.scoreboard.obj("fake202").get())
    }
    ents.say_hi()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"execute as .* run function [^: ]+:generated/internal_root/mchy_func/say_hi_entity/s1/run"
    ), "A command calling the function cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
