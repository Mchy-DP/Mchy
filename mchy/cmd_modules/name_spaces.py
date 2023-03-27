from typing import Dict, List, Optional, Set
from typing import Dict, Optional, Set
from mchy.cmd_modules.chains import IChain, IChainLink

from mchy.cmd_modules.function import IFunc
from mchy.cmd_modules.properties import IProp
from mchy.cmd_modules.struct import IStruct


class Namespace:

    namespaces: Dict[str, 'Namespace'] = {}

    def __init__(self, name: str, parent_ns: Optional['Namespace'] = None) -> None:
        self.name: str = name
        self.parent_ns: Optional[Namespace] = parent_ns
        self.children: Set[Namespace] = set()
        if self.parent_ns is not None:
            self.parent_ns.add_child(self)
        else:
            Namespace.namespaces[name] = self

        self.ifuncs: List[IFunc] = []
        self.iprops: List[IProp] = []
        self.ichain_links: List[IChainLink] = []
        self.istructs: List[IStruct] = []

    def add_child(self, ns: 'Namespace') -> None:
        self.children.add(ns)

    def register_new_func(self, func: IFunc) -> None:
        self.ifuncs.append(func)

    def register_new_prop(self, prop: IProp) -> None:
        self.iprops.append(prop)

    def register_new_chain_link(self, chain_link: IChainLink) -> None:
        self.ichain_links.append(chain_link)

    def register_new_struct(self, struct: IStruct) -> None:
        self.istructs.append(struct)

    @staticmethod
    def get_namespace(name: str) -> 'Namespace':
        if name in Namespace.namespaces:
            return Namespace.namespaces[name]
        raise ValueError(f"No namespace named `{name}`")

    def render(self) -> str:
        return ((self.parent_ns.render() + "::" + self.name) if self.parent_ns is not None else self.name)
