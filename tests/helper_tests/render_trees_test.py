
from mchy.mchy_ast.nodes import *
from tests.helpers.render_trees import StrNode, render_tree
import textwrap
import pytest


@pytest.mark.parametrize("tree, expected", [
    (StrNode("a"), "a"),
    (
        StrNode("a", StrNode("b")),
        """
        a
        └b
        """
    ),
    (
        StrNode(
            "minecraft",
            StrNode(
                "saves",
                StrNode("world1"),
                StrNode(
                    "world2",
                    StrNode(
                        "datapacks",
                        StrNode("Portal"),
                        StrNode("Wells"),
                        StrNode("Better_Beacons")
                    )
                ),
                StrNode(
                    "world3",
                    StrNode("datapacks")
                )
            )
        ),
        """
        minecraft
        └saves
         ├world1
         ├world2
         │└datapacks
         │ ├Portal
         │ ├Wells
         │ └Better_Beacons
         └world3
          └datapacks
        """
    ),
])
def test_render_str_trees_correct(tree: StrNode, expected: str):
    assert (tree.render().strip("\n\r") == textwrap.dedent(expected).strip("\n\r"))


@pytest.mark.parametrize("tree, expected", [
    (Root(), "Root()"),
    (
        Root(Stmnt()),
        """
        Root(Stmnt)
        └Stmnt()
        """
    ),
])
def test_render_tree(tree: Node, expected: str):
    assert (render_tree(tree).strip("\n\r") == textwrap.dedent(expected).strip("\n\r"))
