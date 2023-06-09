from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_constants_print():
    code = """
    print("Hello world!")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^(say|tell|tellraw).*Hello world!"
    ), "A say/tell/tellraw command printing Hello world cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_var_decl_assign_and_print():
    code = """
    var x: int = 15
    x = 10
    print(x)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard.*set.*var_x.*15"
    ), "A scoreboard command setting var_x to 15 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard.*set.*var_x.*10"
    ), "A scoreboard command setting var_x to 10 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        vir_dp.load_master_file, r"^(say|tell|tellraw).*var_x"
    ), "A say/tell/tellraw command printing var_x cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_if_stmnt():
    code = """
    var x: int = 32
    var y: bool = True
    if(y){
        x = x + 7
    }
    x = x + 1
    print(x, ", ", y)
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    if_body = get_file_matching_name(vir_dp.extra_frags_init, r"frag_if1")
    passover = get_file_matching_name(vir_dp.extra_frags_init, r"frag_tops1")

    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard.*set.*var_x.*32"
    ), "A scoreboard command setting var_x to 32 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        if_body, r"^scoreboard.*add.*7"
    ), "A scoreboard command adding 7 cannot be found, raw file:\n"+if_body.get_file_data()
    assert any_line_matches(
        passover, r"^scoreboard.*add.*1"
    ), "A scoreboard command adding 1 cannot be found, raw file:\n"+passover.get_file_data()


def test_simple_func_add1():
    code = """
    var y: int = 5
    def add1(x: int) -> int {
        return x + 1
    }
    print(add1(y))
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    add1_s1_fld = get_folder_matching_name(get_folder_matching_name(vir_dp.mchy_func_fld, "add1"), "s1$")
    add1_body = get_file_matching_name(add1_s1_fld, "run")

    # Top level scope checks
    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard.*operation.*param_x.*var_y.*mchy_glob"
    ), "A scoreboard command setting param_x to var_y from global scope cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        vir_dp.load_master_file, r".*function.*mchy_func/add1"
    ), "A function calling add1 cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        vir_dp.load_master_file, r"^scoreboard.*operation.*var_[0-9]+.*mchy_glob.*return"
    ), "A scoreboard command setting a pseudo var in global scope to the function return cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()

    # Func body checks
    assert any_line_matches(
        add1_body, r"^scoreboard.*add.*1"
    ), "A scoreboard command incrementing a variable in the body cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        add1_body, r"^scoreboard.*operation.*return.*="
    ), "A scoreboard command assigning to return cannot be found, raw file:\n"+add1_body.get_file_data()


def test_while_loop():
    code = """
    var x: int = 8
    while x {
        print(x)
        x = x - 1
    }
    print("done!")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    loop_cond = get_file_matching_name(vir_dp.extra_frags_init, r"frag_cond1")
    loop_body = get_file_matching_name(vir_dp.extra_frags_init, r"frag_loop1")
    loop_exit = get_file_matching_name(vir_dp.extra_frags_init, r"frag_tops1")

    assert any_line_matches(
        vir_dp.load_master_file, r".*function.*frag_cond1"
    ), "A function command calling the loop condition cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()
    assert any_line_matches(
        loop_cond, r"^execute.*if score var_x.*function.*frag_loop1"
    ), "A execute command checking var_x and calling frag_loop1 cannot be found, raw file:\n"+loop_cond.get_file_data()
    assert any_line_matches(
        loop_body, r".*function.*frag_cond1"
    ), "A function command calling the loop condition from the loop body cannot be found, raw file:\n"+loop_body.get_file_data()


def _helper_assert_msg(var: str) -> str:
    return f"A tellraw command outputting the variable {var} cannot be found, raw file:\n"


def test_print_all_types():
    code = """
    var a1: str!? = "TEST"
    var a2: str!? = null
    var b1: float!? = 3.14
    var b2: float!? = null
    var c1: int? = 13
    var c2: int? = null
    var c3: int! = 13
    var c4: int = 13
    var d1: bool? = True
    var d2: bool? = null
    var d3: bool! = True
    var d4: bool = True
    var e1: Player = world.get_player().find()
    var e2: Group[Player] = world.get_players().find()
    var e3: Entity = world.get_entity().find()
    var e4: Group[Entity] = world.get_entities().find()

    print("Varaible `a1: str!?`     has value: ", a1, " (Expected: TEST)")
    print("Varaible `a2: str!?`     has value: ", a2, " (Expected: null)")
    print("Varaible `b1: float!?`   has value: ", b1, " (Expected: 3.14)")
    print("Varaible `b2: float!?`   has value: ", b2, " (Expected: null)")
    print("Varaible `c1: int?`      has value: ", c1, " (Expected: 13)")
    print("Varaible `c2: int?`      has value: ", c2, " (Expected: null)")
    print("Varaible `c3: int!`      has value: ", c3, " (Expected: 13)")
    print("Varaible `c4: int`       has value: ", c4, " (Expected: 13)")
    print("Varaible `d1: bool?`     has value: ", d1, " (Expected: True)")
    print("Varaible `d2: bool?`     has value: ", d2, " (Expected: null)")
    print("Varaible `d3: bool!`     has value: ", d3, " (Expected: True)")
    print("Varaible `d4: bool`      has value: ", d4, " (Expected: True)")
    print("Varaible `e1: Player`    has value: ", e1, " (Expected: A player)")
    print("Varaible `e2: G[Player]` has value: ", e2, " (Expected: Many Players)")
    print("Varaible `e3: Entity`    has value: ", e3, " (Expected: A Entity)")
    print("Varaible `e4: G[Entity]` has value: ", e4, " (Expected: Chat Spam)")
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`a1.*TEST.*Expected:"), _helper_assert_msg("a1") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`a2.*<null>.*Expected:"), _helper_assert_msg("a2") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`b1.*3.14.*Expected:"), _helper_assert_msg("b1") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`b2.*<null>.*Expected:"), _helper_assert_msg("b2") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`c1.*score.*var_c1.*glob.*Expected:"), _helper_assert_msg("c1") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`c2.*<null>.*Expected:"), _helper_assert_msg("c2") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`c3.*13.*Expected:"), _helper_assert_msg("c3") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`c4.*score.*var_c4.*glob.*Expected:"), _helper_assert_msg("c4") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`d1.*score.*var_d1.*glob.*Expected:"), _helper_assert_msg("d1") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`d2.*<null>.*Expected:"), _helper_assert_msg("d2") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`d3.*(1|True|true).*Expected:"), _helper_assert_msg("d3") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`d4.*score.*var_d4.*glob.*Expected:"), _helper_assert_msg("d4") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`e1.*selector.*@a.*var_e1.*limit=1.*Expected:"), _helper_assert_msg("e1") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`e2.*selector.*@a.*var_e2.*Expected:"), _helper_assert_msg("e2") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`e3.*selector.*@e.*var_e3.*limit=1.*Expected:"), _helper_assert_msg("e3") + vir_dp.load_master_file.get_file_data()
    assert any_line_matches(vir_dp.load_master_file, r"^tellraw.*`e4.*selector.*@e.*var_e4.*Expected:"), _helper_assert_msg("e4") + vir_dp.load_master_file.get_file_data()


def test_simple_getting_entities():
    code = """
    var foo: Group[Entity] = world.get_entities().of_type("minecraft:creeper").find()
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    assert any_line_matches(
        vir_dp.load_master_file, r"^tag.*add.*var_foo"
    ), "A tag command adding a tag containing var_foo cannot be found, raw file:\n"+vir_dp.load_master_file.get_file_data()


def test_func_this_treatment():
    code = """
    def Player make_stand(){
        let stand: Entity = world.summon(this.pos.get(), "minecraft:armor_stand")
        stand.rotate.match(this)
    }
    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)

    make_stand_func = get_file_matching_name(get_folder_matching_name(get_folder_matching_name(vir_dp.mchy_func_fld, r"make_stand_player"), r"s0"), r"run\.mcfunction")

    assert any_line_matches(
        make_stand_func, r"""^execute as @e\[.*var_stand.*\] at @s rotated as @a\[.*var_[0-9]+.*\] run tp \^ \^ \^"""
    ), "A command with correct treatment of this cannot be found, raw file:\n"+make_stand_func.get_file_data()
