from mchy.cmd_modules.name_spaces import Namespace
from os import path as os_path

from mchy.contextual.struct.expr.abs_node import CtxExprLits


DOCS_LIBS_DIR = os_path.join(os_path.dirname(os_path.dirname(__file__)), "docs", "libs")


def generate_doc(ns: Namespace) -> str:
    out = f"# {ns.render()}\n"
    # Functions
    out += "## Functions\n"
    for func in ns.ifuncs:
        func_out = f"### {func.get_name()}\n"
        func_out += f"```\n{func.get_name()}("
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
    
    return out


for namespace_name, ns in Namespace.namespaces.items():
    file_text = generate_doc(ns)
    with open(os_path.join(DOCS_LIBS_DIR, f"{namespace_name}.md"), 'w') as file:
        file.write(file_text)
