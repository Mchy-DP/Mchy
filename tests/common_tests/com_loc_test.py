
import pytest
from mchy.common.com_loc import ComLoc
from tests.helpers.diff_locs import loc_diff


@pytest.mark.parametrize("left, right, expected", [
    (ComLoc(), ComLoc(), ComLoc()),
    (ComLoc(1), ComLoc(), ComLoc(1)),
    (ComLoc(1, 2), ComLoc(), ComLoc(1, 2)),
    (ComLoc(1, 2, 3), ComLoc(), ComLoc(1, 2, 3)),
    (ComLoc(1, 2, 3, 4), ComLoc(), ComLoc(1, 2, 3, 4)),
    (ComLoc(1, 0, 1, 5), ComLoc(1, 2, 1, 7), ComLoc(1, 0, 1, 7)),  # overlap
    (ComLoc(1, 0, 1, 3), ComLoc(1, 6, 1, 7), ComLoc(1, 0, 1, 7)),  # disjoint
    (ComLoc(1, 0, 2, 3), ComLoc(1, 6, 1, 7), ComLoc(1, 0, 2, 3)),  # l-line
    (ComLoc(1, 0, 1, 3), ComLoc(1, 6, 2, 7), ComLoc(1, 0, 2, 7)),  # r-line
])
def test_col_union(left: ComLoc, right: ComLoc, expected: ComLoc):
    loc_union_lr = left.union(right)
    assert loc_union_lr == expected, f"{loc_union_lr} != {expected}; LR-diff: " + loc_diff(loc_union_lr, expected)
    loc_union_rl = right.union(left)
    assert loc_union_rl == expected, f"{loc_union_rl} != {expected}; RL-diff:" + loc_diff(loc_union_rl, expected)
