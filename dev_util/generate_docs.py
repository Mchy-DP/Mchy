# Ensure Mchy on path:
import sys
from os import path as os_path

from mchy.common.com_types import ExecCoreTypes, ExecType
from mchy.errors import UnreachableError
sys.path.append(os_path.dirname(os_path.dirname(__file__)))
# Perform Required imports
from mchy.cmd_modules.name_spaces import Namespace  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible
from mchy.contextual.struct.expr.abs_node import CtxExprLits  # noqa  #  pycodestyle doesn't like imports after ANY code even when sensible


DOCS_LIBS_DIR = os_path.join(os_path.dirname(os_path.dirname(__file__)), "docs", "libs")


def executor_prefix(exec_type: ExecType, postfix: str) -> str:
    if exec_type.target == ExecCoreTypes.WORLD:
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


def generate_doc(ns: Namespace) -> str:
    out = f"# {ns.render()}\n"
    # Functions
    out += "## Functions\n"
    for func in sorted(ns.ifuncs, key=lambda x: x.get_name()):
        func_out = f"### {func.get_name()}\n"
        func_out += f"```\n{executor_prefix(func.get_executor_type(), '.')}{func.get_name()}("
        for param in func.get_params():
            func_out += f"{param.label}: {param.param_type.render()}"
            if isinstance(param.default_ctx_expr, CtxExprLits):
                func_out += " = "
                if hasattr(param.default_ctx_expr, "value"):
                    func_out += str(param.default_ctx_expr.value)  # type: ignore  # False positive due to mypy not understanding hasattr
                else:
                    default_name = type(param.default_ctx_expr).__name__
                    if default_name.startswith("CtxExprLit"):
                        func_out += default_name.removeprefix("CtxExprLit").lower()
                    else:
                        func_out += "..."
            func_out += ", "
        func_out = func_out.rstrip(", ")
        func_out += f") -> {func.get_return_type().render()}\n```\n"
        out += func_out
    # Properties
    out += "## Properties\n"
    for prop in sorted(ns.iprops, key=lambda x: x.get_name()):
        prop_out = f"### {prop.get_name()}\n"
        prop_out += f"```\n{executor_prefix(prop.get_executor_type(), '.')}{prop.get_name()} -> {prop.get_prop_type().render()}\n```\n"
        out += prop_out
    return out


for namespace_name, ns in Namespace.namespaces.items():
    file_text = generate_doc(ns)
    with open(os_path.join(DOCS_LIBS_DIR, f"{namespace_name}.md"), 'w') as file:
        file.write(file_text)
