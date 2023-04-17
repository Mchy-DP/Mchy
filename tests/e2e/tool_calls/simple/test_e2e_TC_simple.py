from tests.e2e.tool_calls.helper import E2eData, MakeState, get_proj_based_path, setup_test


def test_e2e():
    # setup test
    e2e_data: E2eData = setup_test(__file__)

    # run test
    with MakeState([
                get_proj_based_path("mchy", "__main__.py"),
                "-o", e2e_data.dp_dir,
                e2e_data.mchy_file
            ]):
        import mchy.__main__

    # check output good
    assert e2e_data.dp_file_exists(["generated.txt"]), "Couldn't find: " + e2e_data.debug_last_queried_filepath
