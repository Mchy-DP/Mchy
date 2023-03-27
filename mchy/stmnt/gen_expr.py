from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
from mchy.cmd_modules.function import CtxIFunc, CtxIParam

from mchy.common.abs_ctx import AbsCtxParam
from mchy.common.com_types import ExecType, InertCoreTypes, InertType, StructType
from mchy.common.config import Config
from mchy.contextual.struct.ctx_func import CtxMchyFunc, CtxMchyParam
from mchy.contextual.struct.expr import *
from mchy.contextual.struct.expr.structs import CtxPyStructInstance
from mchy.errors import ConversionError, StatementRepError, UnreachableError
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtPseudoVar, SmtPublicVar, SmtStruct
from mchy.stmnt.struct.cmds import *
from mchy.stmnt.struct.function import SmtFunc, SmtMchyFunc
from mchy.stmnt.struct.struct import SmtPyStructInstance

if TYPE_CHECKING:
    from mchy.stmnt.struct.module import SmtModule


def convert_expr(ctx_expr: CtxExprNode, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    """Convert the expression tree `ctx_expr` from module `module` and function `function` to statement representation.

    Args:
        ctx_expr: The context tree to convert
        module: The module this expression will be added to (For atom linking)
        function: The function this expression will be added into (For correct var scoping)

    Returns:
        Tuple[List[SmtCmd], SmtAtom]:
          * return[0] -> The list of commands required for the output atom to hold the correct value.
          * return[1] -> The output atom that the result of this expression will be found in.
    """
    _my_type = ctx_expr.get_type()
    if isinstance(_my_type, InertType):
        if _my_type.is_intable():
            return convert_intable_expr(ctx_expr, module, function, config=config)
        else:
            return convert_gen_inert_expr(ctx_expr, module, function, config=config)
    elif isinstance(_my_type, ExecType):
        return convert_exec_expr(ctx_expr, module, function, config=config)
    elif isinstance(_my_type, StructType):
        return convert_struct_expr(ctx_expr, module, function, config=config)
    else:
        raise StatementRepError(f"Unknown typeclass {repr(_my_type)}")


def convert_intable_expr(ctx_expr: CtxExprNode, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    if isinstance(ctx_expr, CtxExprFuncCall):
        return convert_func_call_expr(ctx_expr, module, function, config=config)
    elif isinstance(ctx_expr, CtxExprPropertyAccess):
        source_cmds, source_holder = convert_expr(ctx_expr.source, module, function, config=config)
        prop_cmds, prop_holder = ctx_expr.prop.stmnt_conv(source_holder, module, function, config=config)
        return source_cmds + prop_cmds, prop_holder
    elif isinstance(ctx_expr, CtxExprPartialChain):
        raise StatementRepError(f"Cannot convert partial chains (chain={ctx_expr.render()})")
    elif isinstance(ctx_expr, CtxExprFinalChain):
        return convert_chain_expr(ctx_expr, module, function, config)
    elif isinstance(ctx_expr, CtxExprExponent):
        return convert_int_exponent_expr(ctx_expr, module, function, config=config)
    elif isinstance(ctx_expr, CtxExprDiv):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.numerator, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.denominator, module, function, config=config)
        return (
            left_cmds + [SmtAssignCmd(register1, left_holder)] +
            right_cmds + [SmtDivCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprMod):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.divisor, module, function, config=config)
        return (
            left_cmds + [SmtAssignCmd(register1, left_holder)] +
            right_cmds + [SmtModCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprMult):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + [SmtAssignCmd(register1, left_holder)] +
            right_cmds + [SmtMultCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprMinus):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + [SmtAssignCmd(register1, left_holder)] +
            right_cmds + [SmtMinusCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprPlus):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + [SmtAssignCmd(register1, left_holder)] +
            right_cmds + [SmtPlusCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprCompEquality):
        output_register = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtCompEqualityCmd(
                # Normal inputs
                left_holder, right_holder, output_register,
                # Clobber registers
                function.new_pseudo_var(InertType(InertCoreTypes.INT)), function.new_pseudo_var(InertType(InertCoreTypes.INT)),
                function.new_pseudo_var(InertType(InertCoreTypes.INT)), function.new_pseudo_var(InertType(InertCoreTypes.INT))
            )]
        ), output_register
    elif isinstance(ctx_expr, CtxExprCompGTE):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtCompGTECmd(left_holder, right_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprCompGT):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtCompGTCmd(left_holder, right_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprCompLTE):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtCompGTECmd(right_holder, left_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprCompLT):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtCompGTCmd(right_holder, left_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprNot):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        expr_cmds, expr_holder = convert_expr(ctx_expr.target, module, function, config=config)
        return (
            expr_cmds + [SmtNotCmd(expr_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprAnd):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtAndCmd(right_holder, left_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprOr):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + right_cmds + [SmtOrCmd(right_holder, left_holder, register1)]
        ), register1
    elif isinstance(ctx_expr, CtxExprNullCoal):
        output_register = function.new_pseudo_var(ctx_expr.get_type())
        opt_cmds, opt_holder = convert_expr(ctx_expr.opt_expr, module, function, config=config)
        def_cmds, def_holder = convert_expr(ctx_expr.default_expr, module, function, config=config)
        return (
            opt_cmds + def_cmds + [SmtNullCoalCmd(
                # Normal inputs
                opt_holder, def_holder, output_register,
                # Clobber registers
                function.new_pseudo_var(InertType(InertCoreTypes.INT)), function.new_pseudo_var(InertType(InertCoreTypes.INT)),
                function.new_pseudo_var(InertType(InertCoreTypes.INT)), function.new_pseudo_var(InertType(InertCoreTypes.INT)),
                function.new_pseudo_var(InertType(InertCoreTypes.INT)),
                # Null source (constant)
                module.get_null_const()
            )]
        ), output_register
    elif isinstance(ctx_expr, CtxExprVar):
        return convert_var_expr(ctx_expr, module, function)
    elif isinstance(ctx_expr, CtxExprPyStruct):
        raise StatementRepError(f"Struct encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitStr):
        raise StatementRepError(f"String encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitInt):
        return [], module.get_const_with_val(ctx_expr.value)
    elif isinstance(ctx_expr, CtxExprLitFloat):
        raise StatementRepError(f"Float encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitNull):
        raise StatementRepError(f"Null encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitWorld):
        raise StatementRepError(f"World encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitThis):
        raise StatementRepError(f"This encountered in integer expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitBool):
        return [], module.get_const_with_val(int(ctx_expr.value))
    else:
        raise UnreachableError(f"Unhandled CtxExprNode subclass `{type(ctx_expr).__name__}` in integer convert expression")


def convert_gen_inert_expr(ctx_expr: CtxExprNode, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    if isinstance(ctx_expr, CtxExprFuncCall):
        return convert_func_call_expr(ctx_expr, module, function, config=config)
    elif isinstance(ctx_expr, CtxExprPropertyAccess):
        source_cmds, source_holder = convert_expr(ctx_expr.source, module, function, config=config)
        prop_cmds, prop_holder = ctx_expr.prop.stmnt_conv(source_holder, module, function, config=config)
        return source_cmds + prop_cmds, prop_holder
    elif isinstance(ctx_expr, CtxExprPartialChain):
        raise StatementRepError(f"Cannot convert partial chains (chain={ctx_expr.render()})")
    elif isinstance(ctx_expr, CtxExprFinalChain):
        return convert_chain_expr(ctx_expr, module, function, config)
    elif isinstance(ctx_expr, (CtxExprExponent, CtxExprDiv, CtxExprMod, CtxExprMult, CtxExprMinus, CtxExprPlus)):
        raise StatementRepError(f"Math operations are not valid on general inert types -> Only on types that can be implicitly cast to int")
    elif isinstance(ctx_expr, (CtxExprCompEquality, CtxExprCompGTE, CtxExprCompGT, CtxExprCompLTE, CtxExprCompLT)):
        raise StatementRepError(f"Comparison operations are not valid on general inert types -> Only on types that can be implicitly cast to int")
    elif isinstance(ctx_expr, CtxExprVar):
        return convert_var_expr(ctx_expr, module, function)
    elif isinstance(ctx_expr, CtxExprPyStruct):
        raise StatementRepError(f"Struct encountered in inert non-intable expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitStr):
        return [], module.get_str_const(ctx_expr.value)
    elif isinstance(ctx_expr, CtxExprLitInt):
        raise StatementRepError(f"Int encountered in non-intable expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitFloat):
        return [], module.get_float_const(ctx_expr.value)
    elif isinstance(ctx_expr, CtxExprLitNull):
        return [], module.get_null_const()
    elif isinstance(ctx_expr, CtxExprLitWorld):
        raise StatementRepError(f"World encountered in inert expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitThis):
        raise StatementRepError(f"This encountered in inert expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitBool):
        raise StatementRepError(f"Bool encountered in non-intable expr parsing?")
    else:
        raise UnreachableError(f"Unhandled CtxExprNode subclass `{type(ctx_expr).__name__}` in generalized inert convert expression")


def convert_exec_expr(ctx_expr: CtxExprNode, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    if isinstance(ctx_expr, CtxExprFuncCall):
        return convert_func_call_expr(ctx_expr, module, function, config=config)
    elif isinstance(ctx_expr, CtxExprPropertyAccess):
        source_cmds, source_holder = convert_expr(ctx_expr.source, module, function, config=config)
        prop_cmds, prop_holder = ctx_expr.prop.stmnt_conv(source_holder, module, function, config=config)
        return source_cmds + prop_cmds, prop_holder
    elif isinstance(ctx_expr, CtxExprPartialChain):
        raise StatementRepError(f"Cannot convert partial chains (chain={ctx_expr.render()})")
    elif isinstance(ctx_expr, CtxExprFinalChain):
        return convert_chain_expr(ctx_expr, module, function, config)
    elif isinstance(ctx_expr, (CtxExprExponent, CtxExprDiv, CtxExprMod, CtxExprMult)):
        raise StatementRepError(f"General math operations are not valid on executable types")
    elif isinstance(ctx_expr, CtxExprPlus):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + [SmtTagMergeCmd(register1, left_holder)] +
            right_cmds + [SmtTagMergeCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprMinus):
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        left_cmds, left_holder = convert_expr(ctx_expr.left, module, function, config=config)
        right_cmds, right_holder = convert_expr(ctx_expr.right, module, function, config=config)
        return (
            left_cmds + [SmtTagMergeCmd(register1, left_holder)] +
            right_cmds + [SmtTagRemoveCmd(register1, right_holder)]
        ), register1
    elif isinstance(ctx_expr, CtxExprVar):
        return convert_var_expr(ctx_expr, module, function)
    elif isinstance(ctx_expr, CtxExprPyStruct):
        raise StatementRepError(f"Struct encountered in inert non-intable expr parsing?")
    elif isinstance(ctx_expr, (CtxExprLitStr, CtxExprLitInt, CtxExprLitFloat, CtxExprLitBool, CtxExprLitNull)):
        raise StatementRepError(f"Inert Literal encountered in executable expr parsing?")
    elif isinstance(ctx_expr, CtxExprLitWorld):
        return [], module.get_world()
    elif isinstance(ctx_expr, CtxExprLitThis):
        if isinstance(function, SmtMchyFunc):
            return [], function.executor_var
        else:
            raise StatementRepError(f"`this` outside of mchy function (Enclosing function of type: `{type(function)}`)")
    else:
        raise UnreachableError(f"Unhandled CtxExprNode subclass `{type(ctx_expr).__name__}` in generalized executable convert expression")


def convert_struct_expr(ctx_expr: CtxExprNode, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    if isinstance(ctx_expr, CtxExprPyStruct):
        return convert_struct_instance(ctx_expr.struct_instance, module, function, config)
    elif isinstance(ctx_expr, CtxExprVar):
        raise StatementRepError(f"Variable `{repr(ctx_expr)}` of struct-type not flattened by statement layer?")
    else:
        raise StatementRepError(f"Compound tag `{repr(ctx_expr)}` found at statement-level struct parsing?")


def convert_var_expr(ctx_expr: CtxExprVar, module: 'SmtModule', function: SmtFunc) -> Tuple[List[SmtCmd], SmtAtom]:
    if ctx_expr.var.declaration_marker.enclosing_function is None:
        declaration_func_scope = module.initial_function
    else:
        declaration_func_scope = module.get_smt_func(ctx_expr.var.declaration_marker.enclosing_function)
    return [], declaration_func_scope.new_public_var(ctx_expr.var.name, ctx_expr.get_type())


def generate_atom_param_binding(
            params: Dict[AbsCtxParam, Optional[CtxExprNode]],
            source_err_str: str,
            module: 'SmtModule',
            function: SmtFunc,
            config: Config
        ) -> Tuple[List[SmtCmd], Dict[AbsCtxParam, Optional[SmtAtom]]]:
    param_atom_binding: Dict[AbsCtxParam, Optional[SmtAtom]] = {}
    cmds: List[SmtCmd] = []
    for param, in_line_value in params.items():
        if in_line_value is not None:
            param_cmds, param_atom = convert_expr(in_line_value, module, function, config=config)
            cmds.extend(param_cmds)
            param_atom_binding[param] = param_atom
        else:
            if param.is_defaulted():
                param_atom_binding[param] = None
            else:
                raise StatementRepError(f"Param `{param.render()}` has no value for call of function `{source_err_str}`")
    return cmds, param_atom_binding


def convert_func_call_expr(ctx_expr: CtxExprFuncCall, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    cmds: List[SmtCmd] = []
    # Aid output datapack readability
    if isinstance(ctx_expr.function, CtxMchyFunc):
        cmds.append(SmtCommentCmd(f"Calling function {ctx_expr.function.get_name()}", importance=CommentImportance.HEADING))
    # Resolve Executor
    executor_cmds, executor_holder = convert_expr(ctx_expr.executor, module, function, config=config)
    cmds.extend(executor_cmds)
    # Solve atom binding for normal params
    arg_cmds, param_atom_binding = generate_atom_param_binding(
        {param: ctx_expr.get_param_value(param) for param in ctx_expr.function.get_params()}, ctx_expr.function.render(), module, function, config
    )
    cmds.extend(arg_cmds)
    # Solve atom binding for extra params (If the exist)
    extra_atom_binding: List[SmtAtom] = []
    for in_line_value in ctx_expr.get_extra_values():
        param_cmds, param_atom = convert_expr(in_line_value, module, function, config=config)
        cmds.extend(param_cmds)
        extra_atom_binding.append(param_atom)
    # Handle function call:
    if isinstance(ctx_expr.function, CtxMchyFunc):
        if ctx_expr.function not in module.ctx_decl_func:
            raise StatementRepError(f"Attempted to call function `{ctx_expr.function.render()}` before definition")
        # Add commands to perform bindings
        smt_func: SmtMchyFunc = module.get_smt_func(ctx_expr.function)
        for param, atom in param_atom_binding.items():
            if not isinstance(param, CtxMchyParam):
                raise UnreachableError(f"Mchy function with non-mchy param of type {type(param)}")
            param_var: SmtPublicVar = smt_func.param_var_lookup[param.get_label()]
            if atom is None:
                cmds.append(SmtSpecialStackIncTargetAssignCmd(param_var, smt_func.param_default_lookup[param.get_label()]))
            else:
                cmds.append(SmtSpecialStackIncTargetAssignCmd(param_var, atom))
        cmds.append(SmtInvokeFuncCmd(smt_func, executor_holder))
        pseudo_return = function.new_pseudo_var(smt_func.return_var.get_type())
        cmds.append(SmtSpecialStackIncSourceAssignCmd(pseudo_return, smt_func.return_var))
        cmds.append(SmtCommentCmd(f"Call Complete", importance=CommentImportance.HEADING))
        return cmds, pseudo_return
    elif isinstance(ctx_expr.function, CtxIFunc):
        mchy_param_binding: Dict[CtxIParam, SmtAtom] = {}
        for param, atom in param_atom_binding.items():
            if not isinstance(param, CtxIParam):
                raise UnreachableError(f"Imported function with non-imported param of type {type(param)}")
            if atom is None:
                pdefault = module.get_ifunc_param_default_atom(param, config)
                if pdefault is None:
                    raise StatementRepError(f"Param `{param.render()}` is relying on a default that doesn't exist for function `{ctx_expr.function.render()}`")
                mchy_param_binding[param] = pdefault
            else:
                mchy_param_binding[param] = atom
        func_cmds, func_return_holder = ctx_expr.function.stmnt_conv(executor_holder, mchy_param_binding, extra_atom_binding, module, function, config=config)
        cmds.extend(func_cmds)
        return cmds, func_return_holder
    else:
        raise UnreachableError(f"Unhandled subclass of AbsCtxFunc `{type(ctx_expr.function).__name__}`")


def convert_chain_expr(ctx_chain: CtxExprFinalChain, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    cmds: List[SmtCmd] = []
    # Resolve Executor
    executor_cmds, executor_holder = convert_expr(ctx_chain.executor, module, function, config=config)
    cmds.extend(executor_cmds)
    # Solve atom binding for params
    link_param_atom_binding: Dict[CtxChainLink, Tuple[Dict[AbsCtxParam, SmtAtom], List[SmtAtom]]] = {}
    for link in ctx_chain.get_chain_links():
        arg_cmds, param_atom_binding = generate_atom_param_binding(
            {param: link.get_arg_for_param(param) for param in link.get_ctx_params()}, ctx_chain.render(), module, function, config
        )
        cmds.extend(arg_cmds)
        link_param_atom_binding[link] = ({}, [])
        for param, atom in param_atom_binding.items():
            if atom is None:
                # This can only be None if the input is None which it na never be as `.get_arg_for_param()` never returns None
                raise StatementRepError("None argument received from arg binding which can never be None source?")
            link_param_atom_binding[link][0][param] = atom
        for in_line_value in link.get_extra_args():
            param_cmds, param_atom = convert_expr(in_line_value, module, function, config=config)
            cmds.extend(param_cmds)
            link_param_atom_binding[link][1].append(param_atom)
    # Handle Call
    chain_cmds, chain_return_holder = ctx_chain.stmnt_conv(executor_holder, link_param_atom_binding, module, function, config=config)
    cmds.extend(chain_cmds)
    return cmds, chain_return_holder


def convert_struct_instance(struct_instance: CtxPyStructInstance, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    cmds: List[SmtCmd] = []
    field_binding: Dict[str, Any] = {}
    for field in struct_instance.fields:
        try:
            fvalue = struct_instance.get_field_data(field)
        except KeyError:
            continue
        if isinstance(fvalue, CtxExprNode):
            field_cmds, field_holder = convert_expr(fvalue, module, function, config)
            cmds.extend(field_cmds)
            field_binding[field.label] = field_holder
        else:
            field_binding[field.label] = fvalue
    return cmds, SmtStruct(SmtPyStructInstance(struct_instance.get_type(), field_binding))


def convert_int_exponent_expr(ctx_expr: CtxExprExponent, module: 'SmtModule', function: SmtFunc, config: Config) -> Tuple[List[SmtCmd], SmtAtom]:
    base_cmds, base_holder = convert_expr(ctx_expr.base, module, function, config=config)
    if isinstance(ctx_expr.exponent, (CtxExprLitInt, CtxExprLitBool)):
        # TODO: in debug mode this is a good place for a runtime check as it is very easy to hit the int limit with exponents
        exp_val_left = int(ctx_expr.exponent.value)
        register1 = function.new_pseudo_var(ctx_expr.get_type())
        cmds: List[SmtCmd] = [SmtAssignCmd(register1, module.get_const_with_val(1))]
        while exp_val_left > 0:
            exp_val_left -= 1
            cmds.append(SmtMultCmd(register1, base_holder))
        return base_cmds + cmds, register1
    else:
        raise ConversionError("Non-compile constant exponents are not supported")
