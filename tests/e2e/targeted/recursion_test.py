
from tests.e2e.targeted.helpers import any_line_matches, conversion_helper, get_file_matching_name, get_folder_matching_name

import pytest


def test_recursion_factorial():
    code = """

    def recursive_sum(n: int) -> int{
        if n == 0 {
            return 0
        } else {
            return n + recursive_sum(n - 1)
        }
    }

    print("Got: ", recursive_sum(300), " Expected 45150")

    """
    ast_root, ctx_module, smt_module, vir_dp = conversion_helper(code)
    # This test passes so long as converting recursive functions does not yield any error
