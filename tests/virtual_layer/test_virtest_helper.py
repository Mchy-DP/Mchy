
from typing import List
import pytest

from tests.virtual_layer.helper import helper_extract_lines_between


@pytest.mark.parametrize("text, start, stop, match, expected", [
    ("1\n2\n3\n4\n5\n6\n7\n", "2", "4", True, ["3"]),
    ("1\n2\n3\n4\n5\n6\n7\n", "2", "5", True, ["3", "4"]),
    ("1\n2\n3\n4\n5\n6\n7\n", "3", "4", True, []),
    ("1\n2\n3\n4\n5\n6\n7\n", "a", "b", True, []),
    ("1\n2\n3\n4\n5\n6\n7\n", "7", "b", True, []),
    ("1\n2\n3\n4\n5\n6\n7\n", "a", "5", True, []),
    ("1\n2\n3\n4\n5\n6\n7\n", "1", "b", True, ["2", "3", "4", "5", "6", "7"]),
    ("1234\n5678\n90ab\ncdef\nghij", "67", "de", True, []),
    ("1234\n5678\n90ab\ncdef\nghij", "67", "de", False, ["90ab"]),
])
def test_relevant_lines_extracted_correctly(text: str, start: str, stop: str, match: bool, expected: List[str]):
    assert helper_extract_lines_between(text.strip("\n\r \t"), start, stop, complete_match=match) == expected, "relevant lines incorrectly extracted"
