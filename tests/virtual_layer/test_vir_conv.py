from mchy.common.com_types import InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.stmnt.struct import SmtModule, SmtConstStr
from mchy.stmnt.struct.atoms import SmtConstInt
from mchy.stmnt.struct.cmds import SmtAssignCmd, SmtMultCmd, SmtPlusCmd, SmtMinusCmd, SmtModCmd, SmtDivCmd
from mchy.virtual.generation import convert
from tests.virtual_layer.helper import helper_extract_lines_between
import pytest
import re


def test_plus_conv():
    module = SmtModule()
    pseudo_var_0 = module.initial_function.new_pseudo_var(InertType(InertCoreTypes.INT))
    public_var_foo = module.initial_function.new_public_var("foo", InertType(InertCoreTypes.INT))
    module.initial_function.func_frag.body.extend([
        SmtAssignCmd(pseudo_var_0, SmtConstInt(3)),
        SmtPlusCmd(pseudo_var_0, SmtConstInt(7)),
        SmtAssignCmd(public_var_foo, pseudo_var_0)
    ])

    virtual_dp = convert(module, config=Config(testing_comments=True))

    load_text = virtual_dp.load_master_file.get_file_data()
    lines = helper_extract_lines_between(load_text, "top-level-start", "top-level-end", complete_match=False)

    assert len(lines) > 0, f"No lines generated?  Full-text of load file is:\n\n" + load_text
    assert re.match(r"scoreboard.*set.*var_0.*3.*", lines[0]) is not None, f"First line doesn't set? ({lines[0]})"
    assert re.match(r"scoreboard.*add.*var_0.*7.*", lines[1]) is not None, f"Second line doesn't add? ({lines[1]})"
    assert re.match(r"scoreboard.*operation.*var_foo.*=.*var_0.*", lines[2]) is not None, f"Third line doesn't assign the pseudo var to the public one? ({lines[2]})"


def test_math_conv():
    module = SmtModule()
    pseudo_var_0 = module.initial_function.new_pseudo_var(InertType(InertCoreTypes.INT))
    public_var_foo = module.initial_function.new_public_var("foo", InertType(InertCoreTypes.INT))
    module.initial_function.func_frag.body.extend([
        SmtAssignCmd(pseudo_var_0, SmtConstInt(5)),  # 5
        SmtPlusCmd(pseudo_var_0, SmtConstInt(9)),    # 14 = 5  + 9
        SmtMinusCmd(pseudo_var_0, SmtConstInt(2)),   # 12 = 14 - 2
        SmtDivCmd(pseudo_var_0, SmtConstInt(4)),     # 3  = 12 / 4
        SmtMultCmd(pseudo_var_0, SmtConstInt(5)),    # 15 = 3  * 5
        SmtModCmd(pseudo_var_0, SmtConstInt(8)),     # 7  = 15 % 8
        SmtAssignCmd(public_var_foo, pseudo_var_0)   # 7
    ])

    virtual_dp = convert(module, config=Config(testing_comments=True))

    load_text = virtual_dp.load_master_file.get_file_data()
    lines = helper_extract_lines_between(load_text, "top-level-start", "top-level-end", complete_match=False)

    assert len(lines) > 0, f"No lines generated?  Full-text of load file is:\n\n" + load_text
    assert re.match(r"scoreboard.*set.*var_0.*5.*", lines[0]) is not None, f"Line 1 doesn't set? ({lines[0]})"
    assert re.match(r"scoreboard.*add.*var_0.*9.*", lines[1]) is not None, f"Line 2 doesn't add? ({lines[1]})"
    assert re.match(r"scoreboard.*remove.*var_0.*2.*", lines[2]) is not None, f"Line 3 doesn't minus? ({lines[2]})"
    assert re.match(r"scoreboard.*operation.*var_0.*/=.*c4.*", lines[3]) is not None, f"Line 4 doesn't divide? ({lines[3]})"
    assert re.match(r"scoreboard.*operation.*var_0.*\*=.*c5.*", lines[4]) is not None, f"Line 5 doesn't multiply? ({lines[4]})"
    assert re.match(r"scoreboard.*operation.*var_0.*%=.*c8.*", lines[5]) is not None, f"Line 6 doesn't multiply? ({lines[5]})"
    assert re.match(r"scoreboard.*operation.*var_foo.*=.*var_0.*", lines[6]) is not None, f"Final line doesn't assign the pseudo var to the public one? ({lines[6]})"


def test_nullable_int_var_assign_to_nullable_int_var():
    module = SmtModule()
    public_var_nulla = module.initial_function.new_public_var("nulla", InertType(InertCoreTypes.INT, nullable=True))
    public_var_nullb = module.initial_function.new_public_var("nullb", InertType(InertCoreTypes.INT, nullable=True))
    module.initial_function.func_frag.body.extend([
        SmtAssignCmd(public_var_nulla, public_var_nullb)
    ])

    virtual_dp = convert(module, config=Config(testing_comments=True))

    load_text = virtual_dp.load_master_file.get_file_data()
    lines = helper_extract_lines_between(load_text, "top-level-start", "top-level-end", complete_match=False)

    assert len(lines) > 0, f"No lines generated?  Full-text of load file is:\n\n" + load_text
    assert re.match(r"data.*storage.*var_nulla\.value.*storage.*var_nullb\.value", lines[0]) is not None, f"Line 1 doesn't set value? ({lines[0]})"
    assert re.match(r"data.*storage.*var_nulla\.is_null.*storage.*var_nullb\.is_null", lines[1]) is not None, f"Line 2 doesn't set null-ness? ({lines[1]})"
