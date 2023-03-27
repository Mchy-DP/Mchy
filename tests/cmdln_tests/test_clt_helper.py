
from mchy.common.config import Config
from tests.cmdln_tests.helper import config_diff
import pytest


@pytest.mark.parametrize("num_diffs, conf1, conf2", [
    (0, Config(), Config()),
    (1, Config(project_name="TEST"), Config()),
    (1, Config(project_namespace="TEST"), Config()),
    (1, Config(recursion_limit=42), Config()),
    (1, Config(testing_comments=True), Config()),
    (1, Config(output_path="Not here!"), Config()),
    (1, Config(debug_mode=True), Config()),
    (1, Config(verbosity=Config.Verbosity.QUIET), Config()),
    (1, Config(optimisation=Config.Optimize.O2), Config()),
])
def test_config_diff(conf1: Config, conf2: Config, num_diffs: int):
    diffs = config_diff(conf1, conf2)
    assert len(diffs) == num_diffs, f"Diffs not right: {diffs}"
