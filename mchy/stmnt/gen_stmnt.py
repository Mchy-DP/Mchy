
from typing import List, Tuple, Union
from mchy.common.com_types import InertCoreTypes, InertType, StructType, cast_bool_to_int, matches_type
from mchy.common.config import Config
from mchy.contextual.struct import *
from mchy.errors import StatementRepError, UnreachableError
from mchy.stmnt.gen_expr import convert_expr

from mchy.stmnt.struct import SmtCmd, SmtAssignCmd, SmtFunc, SmtMchyFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtPseudoVar, SmtVar
from mchy.stmnt.struct.cmds import CommentImportance, SmtCommentCmd, SmtCompGTECmd, SmtConditionalInvokeFuncCmd, SmtPlusCmd
from mchy.stmnt.struct.smt_frag import RoutingFlavour, SmtFragment


def convert_stmnts(ctx_stmnts: List[CtxStmnt], module: SmtModule, function: SmtFunc, config: Config, fragment: SmtFragment) -> SmtFragment:
    """Convert a list of ctx statements, returns the active fragment at the end of conversion"""
    active_fragment: SmtFragment = fragment
    for ctx_stmnt in ctx_stmnts:
        smt_cmds, new_active_frag = _convert_stmnt(ctx_stmnt, module, function, config, active_fragment)
        active_fragment.body.extend(smt_cmds)
        active_fragment = new_active_frag
    return active_fragment


def _convert_stmnt(ctx_stmnt: CtxStmnt, module: SmtModule, function: SmtFunc, config: Config, fragment: SmtFragment) -> Tuple[List[SmtCmd], SmtFragment]:
    """Convert the supplied context statement to statement rep form

    Args:
        ctx_stmnt: The statement to convert
        module: The module related to this conversion
        function: The function to register variables with
        config: Config options
        fragment: The current active code fragment

    Returns:
        Tuple[List[SmtCmd], SmtFragment]: A tuple containing the converted commands and the new active fragment
    """
    config.logger.very_verbose(f"SMT: Converting statement `{ctx_stmnt}`")
    if isinstance(ctx_stmnt, CtxAssignment):
        return (convert_assignment(ctx_stmnt, module, function, config=config), fragment)
    elif isinstance(ctx_stmnt, CtxExprHolder):
        return (convert_expr_holder(ctx_stmnt, module, function, config=config), fragment)
    elif isinstance(ctx_stmnt, CtxReturn):
        return (convert_return_ln(ctx_stmnt, module, function, config=config), fragment.add_fragment(RoutingFlavour.DEAD))
    elif isinstance(ctx_stmnt, MarkerDeclFunc):
        return (convert_func_decl(ctx_stmnt, module, function, config=config), fragment)
    elif isinstance(ctx_stmnt, CtxIfStmnt):
        return convert_if_stmnt(ctx_stmnt, module, function, config, fragment)
    elif isinstance(ctx_stmnt, CtxWhileLoop):
        return convert_while_loop(ctx_stmnt, module, function, config, fragment)
    elif isinstance(ctx_stmnt, CtxForLoop):
        return convert_for_loop(ctx_stmnt, module, function, config, fragment)
    elif isinstance(ctx_stmnt, MarkerDeclVar):
        if ctx_stmnt.default_assignment is not None:
            if isinstance(ctx_stmnt.default_assignment.var.var_type, StructType):
                return ([], fragment)  # Cull assignments to struct-types after CTX layer -> all usages of this var should have been replaced with struct literals by now
            return (convert_assignment(ctx_stmnt.default_assignment, module, function, config=config), fragment)
        else:
            return ([], fragment)
    else:
        raise UnreachableError(f"Unhandled context statement type {type(ctx_stmnt)}")


def convert_assignment(ctx_assignment: CtxAssignment, module: SmtModule, function: SmtFunc, config: Config) -> List[SmtCmd]:
    if ctx_assignment.var.declaration_marker.enclosing_function is None:
        declaration_func_scope = module.initial_function
    else:
        declaration_func_scope = module.get_smt_func(ctx_assignment.var.declaration_marker.enclosing_function)
    rhs_conversion, output_var = convert_expr(ctx_assignment.rhs, module, function, config=config)
    if matches_type(cast_bool_to_int(ctx_assignment.var.var_type), output_var.get_type()):
        return rhs_conversion + [SmtAssignCmd(declaration_func_scope.new_public_var(ctx_assignment.var.name, output_var.get_type()), output_var)]
    else:
        raise StatementRepError(
            f"Type of rhs unexpectedly didn't match var type after earlier conformation to the contrary.  " +
            f"({ctx_assignment.var.render()} = {repr(output_var)}: {output_var.get_type()})"
        )


def convert_expr_holder(ctx_expr_holder: CtxExprHolder, module: SmtModule, function: SmtFunc, config: Config) -> List[SmtCmd]:
    expr_conv, output_var = convert_expr(ctx_expr_holder.expr, module, function, config=config)
    return expr_conv


def convert_return_ln(ctx_return_ln: CtxReturn, module: SmtModule, function: SmtFunc, config: Config) -> List[SmtCmd]:
    if not isinstance(function, SmtMchyFunc):
        # This error shouldn't happen usually as the ctx layer error should have caught it
        raise StatementRepError(f"Return outside of mchy function (late-error)")
    cmds: List[SmtCmd] = []
    cmds.append(SmtCommentCmd(f"Beginning Return", importance=CommentImportance.HEADING))
    rhs_conversion, output_var = convert_expr(ctx_return_ln.target, module, function, config=config)
    cmds.extend(rhs_conversion)
    cmds.append(SmtCommentCmd(f"Assigning to return output-var", importance=CommentImportance.SUBHEADING))
    cmds.append(SmtAssignCmd(function.return_var, output_var))
    return cmds


def convert_func_decl(ctx_func_decl: MarkerDeclFunc, module: SmtModule, function: SmtFunc, config: Config) -> List[SmtCmd]:
    output_cmds: List[SmtCmd] = []
    linked_func: SmtMchyFunc = module.get_smt_func(ctx_func_decl.func)
    for param_marker in ctx_func_decl.param_markers:
        if param_marker.param_default is None:
            continue
        expr_conv, output_var = convert_expr(param_marker.param_default, module, function, config=config)
        output_cmds.extend(expr_conv)
        assignment_output = function.new_pseudo_var(output_var.get_type())
        output_cmds.append(SmtAssignCmd(assignment_output, output_var))
        linked_func.param_default_lookup[param_marker.param_name] = assignment_output
    module.ctx_decl_func.add(ctx_func_decl.func)
    return output_cmds


def convert_if_stmnt(ctx_if_stmnt: CtxIfStmnt, module: SmtModule, function: SmtFunc, config: Config, fragment: SmtFragment) -> Tuple[List[SmtCmd], SmtFragment]:
    output_cmds: List[SmtCmd] = []
    conditions: List[Union[SmtConstInt, SmtVar]] = []
    passover_frag = fragment.add_fragment(RoutingFlavour.TOP)  # The fragment used to continue execution after an if statement returns to calling scope
    branch_already_taken = function.new_pseudo_var(InertType(InertCoreTypes.BOOL))
    output_cmds.append(SmtAssignCmd(branch_already_taken, module.get_const_with_val(0)))
    branch_taken_cond_prefix: Tuple[Union[SmtConstInt, SmtVar], bool] = (branch_already_taken, False)

    for branch in ctx_if_stmnt.branches:

        # resolve condition
        cond_exec, cond_out = convert_expr(branch.cond, module, function, config)
        output_cmds.extend(cond_exec)

        if not isinstance(cond_out, (SmtConstInt, SmtVar)):
            raise StatementRepError(f"Statement if condition resolution is not a constant int or a variable, found `{repr(cond_out)}`")

        # create branch
        branch_frag = fragment.add_fragment(RoutingFlavour.IF)
        active_branch_frag = convert_stmnts(branch.exec_body, module, function, config, branch_frag)
        # ensure branch will return to passover if execution reaches the end of the fragment
        active_branch_frag.body.append(SmtConditionalInvokeFuncCmd([(module.get_const_with_val(1), True)], function, passover_frag, module.get_world()))
        # During stack unwinding ensure no extra branches are taken
        active_branch_frag.body.append(SmtAssignCmd(branch_already_taken, module.get_const_with_val(1)))

        # call branch if condition resolved true and no previous condition did
        output_cmds.append(
            SmtConditionalInvokeFuncCmd([branch_taken_cond_prefix] + [(atom, False) for atom in conditions] + [(cond_out, True)], function, branch_frag, module.get_world())
        )

        # Add this to conditions such that future elif branches are only taken if all before them failed
        conditions.append(cond_out)

    # If all conditions resolved false call the passover branch
    output_cmds.append(SmtConditionalInvokeFuncCmd([branch_taken_cond_prefix] + [(atom, False) for atom in conditions], function, passover_frag, module.get_world()))

    return output_cmds, passover_frag


def convert_while_loop(ctx_while: CtxWhileLoop, module: SmtModule, function: SmtFunc, config: Config, fragment: SmtFragment) -> Tuple[List[SmtCmd], SmtFragment]:
    # Build fragments
    loop_cond_check = fragment.add_fragment(RoutingFlavour.COND)
    loop_body_frag = fragment.add_fragment(RoutingFlavour.LOOP)
    loop_exit_frag = fragment.add_fragment(RoutingFlavour.TOP)

    # Populate conditional fragment
    cond_exec, cond_out = convert_expr(ctx_while.cond, module, function, config)
    loop_cond_check.body.extend(cond_exec)
    if not isinstance(cond_out, (SmtConstInt, SmtVar)):
        raise StatementRepError(f"Statement while condition resolution is not a constant int or a variable, found `{repr(cond_out)}`")
    # ORDERING: Because cond_out will not be modified after it resolves false, the superfluous 'branch to loop_body_frag' command on the runtime stack will never be called
    loop_cond_check.body.append(SmtConditionalInvokeFuncCmd([(cond_out, False)], function, loop_exit_frag, module.get_world()))  # If the cond_out is false continue execution
    loop_cond_check.body.append(SmtConditionalInvokeFuncCmd([(cond_out, True)], function, loop_body_frag, module.get_world()))  # If the cond_out is true run the loop body

    # Populate body
    active_loop_frag = convert_stmnts(ctx_while.exec_body, module, function, config, loop_body_frag)
    # Make loop body return to condition
    active_loop_frag.body.append(SmtConditionalInvokeFuncCmd([(module.get_const_with_val(1), True)], function, loop_cond_check, module.get_world()))

    return [
        SmtConditionalInvokeFuncCmd([(module.get_const_with_val(1), True)], function, loop_cond_check, module.get_world()),  # Unconditionally call the cond resolution fragment
    ], loop_exit_frag  # return the post-loop fragment for future statement to be added to


def convert_for_loop(ctx_for: CtxForLoop, module: SmtModule, function: SmtFunc, config: Config, fragment: SmtFragment) -> Tuple[List[SmtCmd], SmtFragment]:
    cmds: List[SmtCmd] = []

    # Build fragments
    loop_cond_check = fragment.add_fragment(RoutingFlavour.COND)
    loop_body_frag = fragment.add_fragment(RoutingFlavour.LOOP)
    loop_exit_frag = fragment.add_fragment(RoutingFlavour.TOP)

    # Resolve upper bound
    upper_exec, upper_out = convert_expr(ctx_for.upper_bound, module, function, config)
    cmds.extend(upper_exec)

    # Get index var atom
    index_exec, index_var = convert_expr(CtxExprVar(ctx_for.index_var, src_loc=ctx_for.index_var_loc), module, function, config)
    if not isinstance(index_var, SmtVar):
        raise StatementRepError(f"Index var of for loop {repr(ctx_for)} unexpectedly not a var?")

    # -- Populate conditional fragment --
    loop_cond_check.body.extend(index_exec)  # Any commands to ensure variable is accessible
    cond_out = function.new_pseudo_var(InertType(InertCoreTypes.BOOL))
    loop_cond_check.body.append(SmtCompGTECmd(upper_out, index_var, cond_out))  # Expr{cond_out = (index_var <= upper_out)}
    # ORDERING: Because cond_out will not be modified after it resolves false, the superfluous 'branch to loop_body_frag' command on the runtime stack will never be called
    loop_cond_check.body.append(SmtConditionalInvokeFuncCmd([(cond_out, False)], function, loop_exit_frag, module.get_world()))  # If the cond_out is false continue execution
    loop_cond_check.body.append(SmtConditionalInvokeFuncCmd([(cond_out, True)], function, loop_body_frag, module.get_world()))  # If the cond_out is true run the loop body

    # -- Populate body --
    active_loop_frag = convert_stmnts(ctx_for.exec_body, module, function, config, loop_body_frag)
    # Increment index and return to condition
    active_loop_frag.body.append(SmtPlusCmd(index_var, module.get_const_with_val(1)))
    active_loop_frag.body.append(SmtConditionalInvokeFuncCmd([(module.get_const_with_val(1), True)], function, loop_cond_check, module.get_world()))

    cmds.append(
        SmtConditionalInvokeFuncCmd([(module.get_const_with_val(1), True)], function, loop_cond_check, module.get_world()),  # Unconditionally call the cond resolution fragment
    )

    return cmds, loop_exit_frag  # return the post-loop fragment for future statement to be added to
