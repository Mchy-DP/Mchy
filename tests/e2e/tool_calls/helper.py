

from dataclasses import dataclass
import sys
import os
from typing import List, Optional


@dataclass
class E2eData:
    mchy_file: str
    dp_dir: str

    _last_queried_filepath: str = "<None>"

    @property
    def dp_name(self) -> str:
        return ".".join(os.path.basename(self.mchy_file).split(".")[:-1]).replace("_", " ").title()

    @property
    def debug_last_queried_filepath(self) -> str:
        return self._last_queried_filepath

    def dp_get_file_path(self, relative_path: List[str]) -> str:
        if not isinstance(relative_path, list):
            raise TypeError(f"relative_path of type {type(relative_path)} not list?")
        self._last_queried_filepath = os.path.join(self.dp_dir, self.dp_name, *relative_path)
        return self._last_queried_filepath

    def dp_file_exists(self, relative_path: List[str]) -> bool:
        return os.path.exists(self.dp_get_file_path(relative_path))

    def dp_get_file_data(self, relative_path: List[str]) -> str:
        file_path = self.dp_get_file_path(relative_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Cannot find the file {file_path}")
        with open(file_path, "r") as file:
            file_data = file.read()
        return file_data


def setup_test(test_file: str) -> E2eData:
    test_dir: str = assert_real_path(os.path.dirname(test_file))
    test_name: str = os.path.basename(test_dir)
    dp_dir: str = os.path.join(test_dir, "dp")
    os.makedirs(dp_dir, exist_ok=True)
    return E2eData(
        mchy_file=os.path.join(test_dir, f"{test_name}.mchy"),
        dp_dir=dp_dir
    )


def get_proj_based_path(*extensions: str):
    return assert_real_path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), *extensions))


def assert_real_path(path: str) -> str:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Tried to get path, couldn't.  Found {path}")
    return path


class MakeState:

    def __init__(self, argv: List[str]) -> None:
        self._requested_argv: List[str] = argv
        self._old_argv: Optional[List[str]] = None

    def __enter__(self):
        self._old_argv = sys.argv
        sys.argv = self._requested_argv

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._old_argv is None:
            raise ValueError("Lost old argv, state cannot be restored")
        sys.argv = self._old_argv
