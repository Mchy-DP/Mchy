

from dataclasses import dataclass
import enum
from typing import Callable, Dict, List, Optional

from mchy.stmnt.struct.abs_cmd import SmtCmd


class RoutingFlavour(enum.Enum):
    IF = enum.auto()
    FUNC = enum.auto()
    LOOP = enum.auto()
    COND = enum.auto()  # Used for conditionally running some other fragment
    TOP = enum.auto()  # Used for fragments continuing top level scope
    DEAD = enum.auto()  # Used as a place to write unreachable code to
    TOPS = enum.auto   # DO NOT USE WILL CAUSE NAME CLASHES WITH TOP COMPRESSOR


@dataclass(frozen=True)
class RoutingNode:
    flavour: RoutingFlavour
    count: int
    abs_line: Optional[int] = None
    rel_line: Optional[int] = None


class SmtFragment:

    def __init__(self, new_frag_callback: Callable[['SmtFragment'], None], route: List[RoutingNode]) -> None:
        self.body: List[SmtCmd] = []
        self._route: List[RoutingNode] = route
        self._routing_count: Dict[RoutingFlavour, int] = {}
        self._new_frag_callback: Callable[['SmtFragment'], None] = new_frag_callback
        self._new_frag_callback(self)

    @property
    def route(self) -> List[RoutingNode]:
        return self._route

    def add_fragment(self, flavour: RoutingFlavour) -> 'SmtFragment':
        if flavour in self._routing_count:
            self._routing_count[flavour] += 1
        else:
            self._routing_count[flavour] = 1
        return SmtFragment(self._new_frag_callback, self._route + [RoutingNode(flavour, self._routing_count[flavour])])

    def get_frag_name(self) -> str:
        frag_name = "frag_"
        top_stack = 0
        for rnode in self._route:
            if rnode.flavour == RoutingFlavour.TOP and rnode.count == 1:
                top_stack += 1
            else:
                if top_stack > 0:
                    frag_name += RoutingFlavour.TOPS.name.lower() + str(top_stack) + "_"
                    top_stack = 0
                frag_name += rnode.flavour.name.lower() + str(rnode.count) + "_"
        if top_stack > 0:
            frag_name += RoutingFlavour.TOPS.name.lower() + str(top_stack) + "_"
        return frag_name.rstrip("_")
