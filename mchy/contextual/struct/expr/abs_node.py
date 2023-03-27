
from abc import ABC, abstractmethod
from itertools import zip_longest
from typing import List, Optional, Sequence, TypeVar
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, InertType

T = TypeVar("T", bound='CtxExprNode')


class CtxExprNode(ABC):

    def __init__(self, children: Sequence['CtxExprNode'], src_loc: ComLoc, **kwargs):
        super().__init__(**kwargs)
        self.children: List[CtxExprNode] = list(children)
        self.__type_cache: Optional[ComType] = None
        self.__loc: ComLoc = src_loc

    @property
    def loc(self) -> ComLoc:
        return self.__loc

    def with_loc(self: T, src_loc: ComLoc) -> T:
        self.__loc = src_loc
        return self

    def get_type(self) -> ComType:
        if self.__type_cache is None:
            self.__type_cache = self._get_type()
        return self.__type_cache

    @abstractmethod
    def _get_type(self) -> ComType:
        ...

    def flatten(self) -> 'CtxExprNode':  # TODO: consider caching if this has already been flattened as flatten *should* be idempotent
        cflat_node = self._flatten_children()

        node_type = cflat_node.get_type()
        if (not isinstance(node_type, CtxExprLits)) and isinstance(node_type, InertType) and node_type.const:
            return cflat_node._flatten_body()  # Non-literals with constant type must be converted to a literal
        return cflat_node

    @abstractmethod
    def _flatten_children(self) -> 'CtxExprNode':
        """Yields a node equivalent to this one but with all children recursively flattened.  Node may be the same or different"""
        ...

    @abstractmethod
    def _flatten_body(self) -> 'CtxExprLits':
        """Flattens the tree below this point to a single literal.  Must be called on a node of compile-constant type."""
        ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([type(child).__name__ for child in self.children])})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CtxExprNode):
            return type(self) == type(other) and all(
                [s_child == o_child for s_child, o_child in zip_longest(self.children, other.children, fillvalue=None)]
            )
        return False


class CtxExprLits(CtxExprNode):
    pass
