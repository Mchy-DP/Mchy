
from typing import Any
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.contextual.struct.module import CtxModule
from mchy.errors import ConversionError


def handle_intercept_partial_chain_options(ctx_module: CtxModule, error: ConversionError, wrapped_data: Any) -> None:
    last_partial_clink: IChainLink = wrapped_data[0]
    continuations = ctx_module.get_cont_of_clink(last_partial_clink)
    terminal_cont = [click for click in continuations if isinstance(click, IChain)]
    if len(terminal_cont) >= 1:
        if len(terminal_cont) == 1:
            error.append_to_msg(f" - Did you forget `.{terminal_cont[0].solo_render(False)}`")
        else:
            error.append_to_msg(f" - Did you mean to complete with: [{', '.join(f'`.{cont.solo_render(False)}`' for cont in terminal_cont)}]")
    elif len(continuations) >= 1:
        # Only show non-terminal continuation if no terminal continuations are available
        error.append_to_msg(f" - Did you mean to continue the chain with: [{', '.join(f'`.{cont.solo_render(False)}`' for cont in continuations)}]")
    else:
        raise ConversionError(f"No valid continuation of {last_partial_clink.render()} - This is likely a problem with the library ({last_partial_clink.get_namespace().render()})")
