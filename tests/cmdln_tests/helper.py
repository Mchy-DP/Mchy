
from mchy.common.config import Config
from typing import List, Tuple
from contextlib import contextmanager
import os


@contextmanager
def change_cwd(path):
    old_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def config_diff(observed: Config, expected: Config) -> List[str]:
    diffs: List[Tuple[str, str, str]] = []
    if observed.project_name != expected.project_name:
        diffs.append(("project name", observed.project_name, expected.project_name))
    if observed.project_namespace != expected.project_namespace:
        diffs.append(("project namespace", observed.project_namespace, expected.project_namespace))
    if observed.recursion_limit != expected.recursion_limit:
        diffs.append(("recursion limit", str(observed.recursion_limit), str(expected.recursion_limit)))
    if observed.testing_comments != expected.testing_comments:
        diffs.append(("testing comments", str(observed.testing_comments), str(expected.testing_comments)))
    # Logger equality not checked
    if observed.output_path != expected.output_path:
        diffs.append(("output path", observed.output_path, expected.output_path))
    if observed.debug_mode != expected.debug_mode:
        diffs.append(("debug mode", str(observed.debug_mode), str(expected.debug_mode)))
    if observed.verbosity != expected.verbosity:
        diffs.append(("verbosity", str(observed.verbosity.name), str(expected.verbosity.name)))
    if observed.optimisation != expected.optimisation:
        diffs.append(("optimisation", str(observed.optimisation.name), str(expected.optimisation.name)))

    diff_str: List[str] = []
    for field, ob, ex in diffs:
        diff_str.append(f"{field}: observed `{ob}` - expected `{ex}`")

    return diff_str
