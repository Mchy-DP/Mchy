
from typing import List
from mchy.cmdln.cmdln_arg_parser import parse_args
from mchy.common.config import Config
from os import path as os_path
from tests.cmdln_tests.helper import config_diff, change_cwd
import pytest


TEST_RES_LOC = os_path.join(os_path.dirname(__file__), "resources")
TEST_OUP_LOC = os_path.join(TEST_RES_LOC, "oup")


@pytest.mark.parametrize("expected_filename, args, expected_config", [
    ("filename.mchy", ["filename.mchy"], Config("Filename", "filename", output_path=TEST_RES_LOC)),
    ("f.mchy", ["f.mchy"], Config("F", "f", output_path=TEST_RES_LOC)),
    ("g.mchy", ["./oup/g.mchy"], Config("G", "g", output_path=TEST_RES_LOC)),
    ("f.mchy", ["-v", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, verbosity=Config.Verbosity.VERBOSE)),
    ("f.mchy", ["-vv", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, verbosity=Config.Verbosity.VV)),
    ("f.mchy", ["-q", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, verbosity=Config.Verbosity.QUIET)),
    ("f.mchy", ["-o", TEST_OUP_LOC, "f.mchy"], Config("F", "f", output_path=TEST_OUP_LOC)),
    ("f.mchy", ["--debug", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, debug_mode=True)),
    ("f.mchy", ["--no-debug", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, debug_mode=False)),
    ("f.mchy", ["-o3", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, optimisation=Config.Optimize.O3)),
    ("f.mchy", ["-o1", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, optimisation=Config.Optimize.O1)),
    ("f.mchy", ["-o0", "f.mchy"], Config("F", "f", output_path=TEST_RES_LOC, optimisation=Config.Optimize.NOTHING)),
])
def test_config_generated_correctly(args: List[str], expected_config: Config, expected_filename: str):
    with change_cwd(TEST_RES_LOC):
        filename, config = parse_args(args)
    assert os_path.basename(filename) == expected_filename
    cdiff = config_diff(config, expected_config)
    assert len(cdiff) == 0, "The following differences were observed:\n" + "\n".join(cdiff)
