from typing import NoReturn, Optional
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.contextual.err_intercepts import handle_intercept_partial_chain_options
from mchy.errors import ConversionError
from mchy.contextual.struct.module import CtxModule
from mchy.mchy_ast.nodes import Root as ASTRoot
from mchy.stmnt.struct.module import SmtModule
from mchy.virtual.vir_dp import VirDP


def perform_intercepts(error: ConversionError, ast_root_node: Optional[ASTRoot], ctx_module: Optional[CtxModule], smt_module: Optional[SmtModule], vir_dp: Optional[VirDP]):
    # make accessors for all stages
    def assert_exists_ast() -> ASTRoot:
        if ast_root_node is not None:
            return ast_root_node
        raise ValueError(f"AST was not defined when requested by error: {repr(error)}")

    def assert_exists_ctx() -> CtxModule:
        if ctx_module is not None:
            return ctx_module
        raise ValueError(f"CTX was not defined when requested by error: {repr(error)}")

    def assert_exists_smt() -> SmtModule:
        if smt_module is not None:
            return smt_module
        raise ValueError(f"SMT was not defined when requested by error: {repr(error)}")

    def assert_exists_vir() -> VirDP:
        if vir_dp is not None:
            return vir_dp
        raise ValueError(f"VIR was not defined when requested by error: {repr(error)}")

    # perform Intercepts
    if (wrapped_data := error.intercept(ConversionError.InterceptFlags.PARTIAL_CHAIN_OPTIONS)):
        handle_intercept_partial_chain_options(assert_exists_ctx(), error, wrapped_data)
