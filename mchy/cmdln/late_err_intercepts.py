from typing import NoReturn, Optional
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.errors import ConversionError
from mchy.contextual.struct.module import CtxModule
from mchy.mchy_ast.nodes import Root as ASTRoot
from mchy.stmnt.struct.module import SmtModule
from mchy.virtual.vir_dp import VirDP


def _pretty_print_chain(chainlink: IChainLink, include_return: bool):
    return (
        chainlink.get_name() +
        ('()' if chainlink.get_params() is not None else '') +
        (f' -> {chainlink.get_chain_type().render()}' if include_return and isinstance(chainlink, IChain) else '')
    )


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
        last_partial_clink: IChainLink = wrapped_data[0]
        continuations = assert_exists_ctx().get_cont_of_clink(last_partial_clink)
        terminal_cont = [click for click in continuations if isinstance(click, IChain)]
        if len(terminal_cont) >= 1:
            if len(terminal_cont) == 1:
                error.append_to_msg(f" - Did you forget `.{_pretty_print_chain(terminal_cont[0], False)}`")
            else:
                error.append_to_msg(f" - Did you mean to complete with: [{', '.join(f'`.{_pretty_print_chain(cont, False)}`' for cont in terminal_cont)}]")
        elif len(continuations) >= 1:
            # Only show non-terminal continuation if no terminal continuations are available
            error.append_to_msg(f" - Did you mean to continue the chain with: [{', '.join(f'`.{_pretty_print_chain(cont, False)}`' for cont in continuations)}]")
        else:
            raise ValueError(f"No valid continuation of {last_partial_clink.render()}")
