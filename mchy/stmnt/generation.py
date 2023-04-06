from typing import List
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct import CtxModule
from mchy.contextual.struct.expr.function import CtxExprExtraParamVal, CtxExprFuncCall
from mchy.contextual.struct.expr.literals import CtxExprLitStr, CtxExprLitWorld
from mchy.contextual.struct.expr.structs import CtxExprPyStruct
from mchy.contextual.struct.stmnt import CtxStmnt
from mchy.errors import StatementRepError
from mchy.library.std.cmd_cmd import SmtRawCmd
from mchy.stmnt.gen_expr import convert_func_call_expr
from mchy.stmnt.gen_stmnt import convert_stmnts
from mchy.stmnt.helpers import runtime_error_tellraw_formatter
from mchy.stmnt.struct.atoms import SmtConstInt
from mchy.stmnt.struct.cmds.assign import SmtAssignCmd
from mchy.stmnt.struct.cmds.raw import SmtConditionalRawCmd
from mchy.stmnt.struct.function import SmtFunc
from mchy.stmnt.struct.module import SmtModule
from mchy.stmnt.struct.smt_frag import SmtFragment


def convert(ctx_module: CtxModule, config: Config) -> SmtModule:
    smt_module = SmtModule()
    config.logger.very_verbose(f"SMT: Registering functions")
    # register functions
    mchy_funcs = ctx_module.get_mchy_functions()
    for mchy_func in mchy_funcs:
        smt_module.register_new_mchy_function(mchy_func)
    # build global scope
    build_global_scope(ctx_module, smt_module, config)
    # build function bodies
    config.logger.very_verbose(f"SMT: Building function bodies")
    for mchy_func in mchy_funcs:
        config.logger.very_verbose(f"SMT: Building body of function `{mchy_func.render()}`")
        smt_mchy_func = smt_module.get_smt_func(mchy_func)
        convert_stmnts(mchy_func.exec_body, smt_module, smt_mchy_func, config, smt_mchy_func.func_frag)
    # handle decorated functions
    handle_ticking(ctx_module, smt_module, config)
    handle_public(ctx_module, smt_module, config)
    # return module
    smt_module.create_all_lazy_variables()
    return smt_module


def handle_ticking(ctx_module: CtxModule, smt_module: SmtModule, config: Config) -> None:
    if config.debug_mode:
        last_tick_failed_var = smt_module.initial_function.new_pseudo_var(InertType(InertCoreTypes.INT))
        smt_module.ticking_function.func_frag.body.append(SmtConditionalRawCmd(
            [(last_tick_failed_var, True), (smt_module.error_state_variable, False)],
            runtime_error_tellraw_formatter(
                "last tick did not complete - is there an infinite loop? Alternatively too many commands in 1 tick, see: `gamerule maxCommandChainLength`"
            )
        ))
        smt_module.ticking_function.func_frag.body.append(SmtAssignCmd(last_tick_failed_var, SmtConstInt(1)))
        smt_module.ticking_function.func_frag.body.append(SmtAssignCmd(smt_module.error_state_variable, SmtConstInt(0)))
    for ticking_func in ctx_module.get_ticking_funcs():
        pseudo_ctx_func_call: CtxExprFuncCall = CtxExprFuncCall(CtxExprLitWorld(src_loc=ComLoc()), ticking_func, [], [], src_loc=ComLoc())
        call_cmds, _ = convert_func_call_expr(pseudo_ctx_func_call, smt_module, smt_module.ticking_function, config)
        smt_module.ticking_function.func_frag.body.extend(call_cmds)
    if config.debug_mode:
        smt_module.ticking_function.func_frag.body.append(SmtAssignCmd(last_tick_failed_var, SmtConstInt(0)))


def handle_public(ctx_module: CtxModule, smt_module: SmtModule, config: Config) -> None:
    ctx_print_func = ctx_module.get_function(ExecType(ExecCoreTypes.WORLD, False), "print")
    if ctx_print_func is None:
        raise StatementRepError("Cannot get print function - has STD library failed to load?")
    ctx_color_struct = ctx_module.get_struct("Color")
    if ctx_color_struct is None:
        raise StatementRepError("Cannot get color struct - has STD library failed to load structs (but did load functions?)?")

    for ctx_pub_func in ctx_module.get_public_funcs():
        smt_pub_func = SmtFunc()
        smt_pub_func.func_frag.body.append(SmtRawCmd(
            r'''tellraw @a ["",{"text":"Manually calling public function `","color":"blue"},{"text":"''' + ctx_pub_func.get_name() +
            r'''","color":"light_purple"},{"text":"`","color":"blue"}]'''
        ))
        pseudo_ctx_func_call: CtxExprFuncCall = CtxExprFuncCall(CtxExprLitWorld(src_loc=ComLoc()), ctx_pub_func, [], [], src_loc=ComLoc())
        pseudo_static_print_prefix: List[CtxExprExtraParamVal] = [
            CtxExprExtraParamVal(ctx_color_struct.get_type(), CtxExprPyStruct(ctx_color_struct, {"color_code": "blue"}), src_loc=ComLoc()),
            CtxExprExtraParamVal(InertType(InertCoreTypes.STR, True), CtxExprLitStr("The function returned: ", src_loc=ComLoc()), src_loc=ComLoc()),
            CtxExprExtraParamVal(ctx_color_struct.get_type(), CtxExprPyStruct(ctx_color_struct, {"color_code": "light_purple"}), src_loc=ComLoc()),
        ]
        pseudo_ctx_func_call_as_eparam = CtxExprExtraParamVal(ctx_pub_func.get_return_type(), pseudo_ctx_func_call, src_loc=ComLoc())
        pseudo_print_ctx_func_call_return = CtxExprFuncCall(
            CtxExprLitWorld(src_loc=ComLoc()),
            ctx_print_func,
            [],
            pseudo_static_print_prefix + [pseudo_ctx_func_call_as_eparam],
            src_loc=ComLoc()
        )
        call_cmds, _ = convert_func_call_expr(pseudo_print_ctx_func_call_return, smt_module, smt_pub_func, config)
        smt_pub_func.func_frag.body.extend(call_cmds)
        smt_module.public_functions[ctx_pub_func.get_name()] = smt_pub_func


def build_global_scope(ctx_module: CtxModule, smt_module: SmtModule, config: Config):
    config.logger.very_verbose(f"SMT: Building global scope statements")
    active_frag: SmtFragment = smt_module.initial_function.func_frag
    if config.debug_mode:
        init_var = smt_module.initial_function.new_pseudo_var(InertType(InertCoreTypes.INT))
        active_frag.body.append(SmtAssignCmd(init_var, SmtConstInt(1)))
    active_frag = convert_stmnts(ctx_module.exec_body, smt_module, smt_module.initial_function, config, active_frag)
    if config.debug_mode:
        active_frag.body.append(SmtAssignCmd(init_var, SmtConstInt(0)))
        smt_module.ticking_function.func_frag.body.append(SmtConditionalRawCmd([(init_var, True), (smt_module.error_state_variable, False)], runtime_error_tellraw_formatter(
            "reload did not complete - is there an infinite loop? Alternatively too many commands in 1 tick, see: `gamerule maxCommandChainLength`"
        )))
        smt_module.ticking_function.func_frag.body.append(SmtAssignCmd(init_var, SmtConstInt(0)))
