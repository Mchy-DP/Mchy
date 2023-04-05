from typing import List, Optional, Sequence

# Ensure Mchy on path:
import sys
from os import path as os_path

from mchy.cmd_modules.param import IParam
sys.path.append(os_path.dirname(os_path.dirname(__file__)))

# Perform Required imports
from mchy.cmd_modules.chains import IChain, IChainLink  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
from mchy.errors import UnreachableError  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
from mchy.cmd_modules.name_spaces import Namespace  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
from mchy.contextual.struct.expr.abs_node import CtxExprLits  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible


DOCS_LIBS_DIR = os_path.join(os_path.dirname(os_path.dirname(__file__)), "docs", "libs")


def executor_prefix(exec_type: ExecType, postfix: str, explicit_world: bool = False) -> str:
    if exec_type.target == ExecCoreTypes.WORLD:
        if explicit_world:
            return "world" + postfix
        else:
            return ""
    elif exec_type.target == ExecCoreTypes.ENTITY:
        if exec_type.group:
            return "Entities" + postfix
        else:
            return "Entity" + postfix
    elif exec_type.target == ExecCoreTypes.PLAYER:
        if exec_type.group:
            return "Players" + postfix
        else:
            return "Player" + postfix
    else:
        raise UnreachableError("Unhandled enum case")


def _build_params_render(params: Sequence[IParam]) -> str:
    params_out = ""
    for param in params:
        params_out += f"{param.label}: {param.param_type.render()}"
        if isinstance(param.default_ctx_expr, CtxExprLits):
            params_out += " = "
            if hasattr(param.default_ctx_expr, "value"):
                params_out += str(param.default_ctx_expr.value)  # type: ignore  # False positive due to mypy not understanding hasattr
            else:
                default_name = type(param.default_ctx_expr).__name__
                if default_name.startswith("CtxExprLit"):
                    params_out += default_name.removeprefix("CtxExprLit").lower()
                else:
                    params_out += "..."
        params_out += ", "
    return params_out.rstrip(", ")


class ChainingTree:

    def __init__(self, link: Optional[IChainLink], initial_children: Sequence['ChainingTree'] = []) -> None:
        self.link: Optional[IChainLink] = link
        self._children: List[ChainingTree] = list(initial_children)
        self.parent: Optional[ChainingTree] = None

    def append(self, tree: 'ChainingTree') -> None:
        self._children.append(tree)
        tree.parent = self

    def _render_link(self) -> str:
        if self.link is None:
            raise ValueError("None link while rendering docs")
        out = f"{self.link.get_name()}"
        params = self.link.get_params()
        if params is not None:
            out += "("+_build_params_render(params)+")"
        return out

    def this_chain(self) -> str:
        if self.parent is not None:
            return self.parent.this_chain() + "." + self._render_link()
        if self.link is not None:
            return "(?)." + self._render_link()
        else:
            return "(?)"

    def render(self, indent: int = 0) -> str:
        out = ""
        indent_str = "  " * indent
        nl = "\n" + indent_str
        if self.link is not None:
            out += f"### {self.link.get_name()}{nl}```{nl}{self.this_chain()}{nl}```\n"
        for child in sorted(self._children, key=lambda x: isinstance(x, ChainingLeaf)):
            out += indent_str + "* " + child.render(indent + 1)
        return out


class ChainingLeaf(ChainingTree):

    def __init__(self, link: IChain):
        super().__init__(link, [])
        self.link: IChain

    def this_chain(self) -> str:
        return executor_prefix(self.link.get_refined_executor(), "", explicit_world=True) + (super().this_chain().removeprefix("(?)"))


def build_chaining_tree(remaining_links: List[IChainLink], base_link: Optional[IChainLink] = None) -> ChainingTree:
    active_links: List[IChainLink] = []
    leftover_links: List[IChainLink] = []
    for link in remaining_links:
        pred_type = link.get_predecessor_type()
        if base_link is None:
            # If this is toplevel: activate all links that act on non-chains
            if isinstance(pred_type, ComType):
                active_links.append(link)
            else:
                leftover_links.append(link)
        else:
            # As this is not toplevel only activate chains whose predecessor is the base_link
            if (not isinstance(pred_type, ComType)) and isinstance(base_link, pred_type):
                active_links.append(link)
            else:
                leftover_links.append(link)

    if isinstance(base_link, IChain):
        if len(active_links) >= 1:
            print("Doc gen warning: active links found on leaf?")
        return ChainingLeaf(base_link)
    else:
        this_tree = ChainingTree(base_link)
        for active_link in active_links:
            this_tree.append(build_chaining_tree(leftover_links, active_link))
        return this_tree


def generate_doc(ns: Namespace) -> str:
    out = ""
    out += (
        "<!--\nWARNING: this file is automatically generated,  if you want to change something here you need to change the DocData " +
        "object associated with the func/prop/etc.  DocData objects can be found in `/mchy/library`\n-->\n"
    )
    out += f"# {ns.render()}\n"
    # Functions
    out += "## Functions\n"
    for func in sorted(ns.ifuncs, key=lambda x: x.get_name()):
        func_out = f"### {func.get_name()}\n"
        func_out += f"```\n{executor_prefix(func.get_executor_type(), '.')}{func.get_name()}("
        func_out += _build_params_render(func.get_params())
        func_out += f") -> {func.get_return_type().render()}\n```\n"
        func_out += func.get_docs().render()
        out += func_out
    # Properties
    out += "## Properties\n"
    for prop in sorted(ns.iprops, key=lambda x: x.get_name()):
        prop_out = f"### {prop.get_name()}\n"
        prop_out += f"```\n{executor_prefix(prop.get_executor_type(), '.')}{prop.get_name()} -> {prop.get_prop_type().render()}\n```\n"
        prop_out += prop.get_docs().render()
        out += prop_out
    # Chained methods
    out += "## Chained methods\n"
    chain_structure: ChainingTree = build_chaining_tree(sorted(ns.ichain_links, key=lambda x: x.get_name()))
    out += chain_structure.render()
    # Structures
    out += "## Structs\n"
    for struct in sorted(ns.istructs, key=lambda x: x.get_name()):
        struct_out = f"* `{struct.get_type().render()}`\n"
        struct_out += ("\n"+struct.get_docs().render()).replace("\n> ", "\n  > ").removeprefix("\n")
        out += struct_out
    return out


for namespace_name, ns in Namespace.namespaces.items():
    file_text = generate_doc(ns)
    with open(os_path.join(DOCS_LIBS_DIR, f"{namespace_name}.md"), 'w') as file:
        file.write(file_text)
