

from mchy.cmd_modules.name_spaces import Namespace


def test_std_lib_loaded():
    ns = Namespace.get_namespace("std")
    assert ns.name == "std"


def test_std_lib_cmd_say_loaded_successfully():
    assert "say" in {ifunc.get_name() for ifunc in Namespace.get_namespace("std").ifuncs}


def test_std_lib_mc_version_loaded_successfully():
    assert "version" in {iprop.get_name() for iprop in Namespace.get_namespace("std").iprops}


def test_std_lib_color_loaded_successfully():
    assert "colors" in {iclink.get_name() for iclink in Namespace.get_namespace("std").ichain_links}
    assert "red" in {iclink.get_name() for iclink in Namespace.get_namespace("std").ichain_links}


def test_std_lib_pos_loaded_successfully():
    assert "Pos" in {istruct.get_name() for istruct in Namespace.get_namespace("std").istructs}


def test_std_lib_no_underscore():
    assert "_" not in {ifunc.get_name() for ifunc in Namespace.get_namespace("std").ifuncs}
    assert "_" not in {iprop.get_name() for iprop in Namespace.get_namespace("std").iprops}
    assert "_" not in {iclink.get_name() for iclink in Namespace.get_namespace("std").ichain_links}
    assert "_" not in {istructs.get_name() for istructs in Namespace.get_namespace("std").istructs}
