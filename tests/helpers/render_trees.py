

from typing import List, Optional
from mchy.mchy_ast.nodes import ExprLitGen, Node
from tests.helpers.util import _Diff_lvl, EscapeColors

_TICK = "✓"
_CROSS = "✕"

_BOX_BUILDING_PIPE = "│"
_BOX_BUILDING_T = "├"
_BOX_BUILDING_L = "└"


class StrNode:

    def __init__(self, text: str, *ichindren: 'StrNode', color: Optional[str] = None) -> None:
        self.text: str = text
        self.children: List[StrNode] = list(ichindren)
        self.color: Optional[str] = color

    def _to_render_lines(self) -> List[str]:
        output_lines = [self.text if self.color is None else EscapeColors.ENDC + self.color + self.text + EscapeColors.ENDC]

        if len(self.children) != 0:
            for child in self.children[:-1]:
                child_lines = child._to_render_lines()
                output_lines.append(_BOX_BUILDING_T + child_lines[0])
                for line in child_lines[1:]:
                    output_lines.append(_BOX_BUILDING_PIPE + line)
            child_lines = self.children[-1]._to_render_lines()
            output_lines.append(_BOX_BUILDING_L + child_lines[0])
            for line in child_lines[1:]:
                output_lines.append(" " + line)

        return output_lines

    def render(self) -> str:
        return "\n".join(self._to_render_lines())


def _tree_diff(node1: Node, node2: Node) -> _Diff_lvl:
    if node1 == node2:
        return _Diff_lvl.MATCH
    if type(node1) != type(node2):
        return _Diff_lvl.MISMATCH
    if len(node1.children) != len(node2.children):
        return _Diff_lvl.PROPERTY
    if isinstance(node1, ExprLitGen) and isinstance(node2, ExprLitGen) and node1._value != node2._value:
        return _Diff_lvl.PROPERTY
    if all(child1 == child2 for child1, child2 in zip(node1.children, node2.children)):
        # If all the children match and we allreddy know this node deons't this node must be the problem
        return _Diff_lvl.UNKNOWN
    return _Diff_lvl.PARTIAL


def _gen_str_tree_diffs(observed: Node, expected: Node, color: bool) -> StrNode:
    diff: _Diff_lvl = _tree_diff(observed, expected)
    children: List[StrNode] = []
    if diff in [_Diff_lvl.PARTIAL, _Diff_lvl.UNKNOWN]:
        # NB: for a partial & unknown match we know the children lengths match
        for child in zip(observed.children, expected.children):
            children.append(_gen_str_tree_diffs(*child, color=color))

    if diff == _Diff_lvl.MATCH:
        return StrNode(str(observed) + " " + _TICK, *children, color=None if not color else EscapeColors.GREEN)
    elif diff == _Diff_lvl.PARTIAL:
        return StrNode(str(observed), *children, color=None if not color else EscapeColors.YELLOW)
    elif diff == _Diff_lvl.PROPERTY:
        return StrNode(f"{str(observed)} !~ {str(expected)}" + " " + _CROSS, *children, color=None if not color else EscapeColors.DARK_RED)
    elif diff == _Diff_lvl.UNKNOWN:
        return StrNode(f"{str(observed)} ?= {str(expected)}" + " " + _CROSS, *children, color=None if not color else EscapeColors.DARK_RED)
    elif diff == _Diff_lvl.MISMATCH:
        return StrNode(f"{str(observed)} != {str(expected)}" + " " + _CROSS, *children, color=None if not color else EscapeColors.RED)
    else:
        raise TypeError("Unhandled enum case")


def render_diff(observed: Node, expected: Node, color: bool) -> str:
    return _gen_str_tree_diffs(observed, expected, color).render()


def _gen_str_tree(tree: Node) -> StrNode:
    return StrNode(str(tree), *list(_gen_str_tree(child) for child in tree.children), color=None)


def render_tree(tree: Node) -> str:
    return _gen_str_tree(tree).render()
