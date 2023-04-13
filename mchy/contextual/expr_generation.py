from typing import Dict, Sequence, Tuple, Union
from mchy.common.abs_ctx import AbsCtxFunc, AbsCtxParam
from mchy.common.com_types import matches_type
from mchy.contextual.struct.expr import *
from mchy.mchy_ast.nodes import *
from mchy.contextual.struct import *
from mchy.errors import ContextualisationError, UnreachableError, ConversionError


def convert_expr(ast_expr: ExprGen, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxExprNode:
    return _convert_expr(ast_expr, executing_type, module, var_scopes).flatten()


def convert_expr_noflat(ast_expr: ExprGen, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxExprNode:
    return _convert_expr(ast_expr, executing_type, module, var_scopes)


def _convert_expr(ast_expr: ExprGen, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxExprNode:
    if not isinstance(ast_expr, ExprGen):
        raise ContextualisationError(f"Malformed AST: expression `{str(ast_expr)}` is not a child of ExprGen")
    if isinstance(ast_expr, ExprFuncCall):
        return convert_func_call(ast_expr, executing_type, module, var_scopes)
    elif isinstance(ast_expr, ExprFragParam):
        raise ContextualisationError(f"Malformed AST: Param somehow outside of function call? ({str(ast_expr)})")
    elif isinstance(ast_expr, ExprPropertyAccess):
        return convert_property_access(ast_expr, executing_type, module, var_scopes)
    elif isinstance(ast_expr, ExprExponent):
        return CtxExprExponent(_convert_expr(ast_expr.base, executing_type, module, var_scopes), _convert_expr(ast_expr.exponent, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprMult):
        return CtxExprMult(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprDiv):
        return CtxExprDiv(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprMod):
        return CtxExprMod(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprPlus):
        return CtxExprPlus(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprMinus):
        return CtxExprMinus(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprEquality):
        return CtxExprCompEquality(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprInequality):
        return CtxExprNot(CtxExprCompEquality(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes)))
    elif isinstance(ast_expr, ExprCompGTE):
        return CtxExprCompGTE(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprCompGT):
        return CtxExprCompGT(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprCompLTE):
        return CtxExprCompLTE(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprCompLT):
        return CtxExprCompLT(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprNot):
        return CtxExprNot(_convert_expr(ast_expr.target, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprAnd):
        return CtxExprAnd(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprOr):
        return CtxExprOr(_convert_expr(ast_expr.left, executing_type, module, var_scopes), _convert_expr(ast_expr.right, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprNullCoal):
        return CtxExprNullCoal(_convert_expr(ast_expr.optional_expr, executing_type, module, var_scopes), _convert_expr(ast_expr.default_expr, executing_type, module, var_scopes))
    elif isinstance(ast_expr, ExprLitIdent):
        return convert_lit_ident(ast_expr, module, var_scopes)
    elif isinstance(ast_expr, ExprLitStr):
        return CtxExprLitStr(ast_expr.value, src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitFloat):
        return CtxExprLitFloat(ast_expr.value, src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitInt):
        return CtxExprLitInt(ast_expr.value, src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitNull):
        return CtxExprLitNull(src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitWorld):
        return CtxExprLitWorld(src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitThis):
        if executing_type is None:
            raise ConversionError("`this` cannot be used outside of function scope").with_loc(ast_expr.loc)
        return CtxExprLitThis(executing_type, src_loc=ast_expr.loc)
    elif isinstance(ast_expr, ExprLitBool):
        return CtxExprLitBool(ast_expr.value, src_loc=ast_expr.loc)
    else:
        raise UnreachableError(f"Unknown ExprGen in contextual conversion ({str(ast_expr)})")


def _ast_func_call_args_parsing(args: Sequence[ExprFragParam]) -> Tuple[List[ExprFragParam], List[ExprFragParam]]:
    """Splits args up into positional arguments and keyword arguments

    Args:
        args: The AST arguments to parse

    Raises:
        ConversionError: If Positional arguments occur after the first keyword argument

    Returns:
        A tuple containing a list of positional arguments followed by a list of keyword arguments
    """
    positional_params: List[ExprFragParam] = []
    keyword_params: List[ExprFragParam] = []
    for ast_param in args:
        if ast_param.label is None:
            if len(keyword_params) != 0:
                raise ConversionError("Positional argument's cannot follow keyword arguments").with_loc(ast_param.loc)
            positional_params.append(ast_param)
        else:
            keyword_params.append(ast_param)
    return positional_params, keyword_params


def _build_arg_param_binding(
            params: List[AbsCtxParam],
            args: Sequence[ExprFragParam],
            allow_extra_args: bool,
            source_err_rep: str,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            calling_location: ComLoc
        ) -> Tuple[Dict[AbsCtxParam, Optional[CtxExprNode]], List[CtxExprNode]]:
    """Convert a list of parameters and a list of supplied arguments into the param-arg bindings

    Args:
        params: The parameters to match against
        args: The supplied arguments
        allow_extra_args: If extra args can be parsed
        source_err_rep: The debug string to be printed when the source of invalid param-args is reffed to in errors
        executing_type & module & var_scopes: Context arguments required for convert_expr

    Returns:
        A tuple containing a dictionary linking params to their arg value (Or None if the default should be used) and a list of any extra args provided
    """
    # Separate parameters into keyword and positional
    positional_args, keyword_args = _ast_func_call_args_parsing(args)

    # initialise bindings
    param_bindings: Dict[AbsCtxParam, Optional[CtxExprNode]] = {}
    extra_bindings: List[CtxExprNode] = []

    # strip off extra args
    if allow_extra_args:
        while len(positional_args) > (len(params) - len(keyword_args)):
            extra_bindings.insert(0, convert_expr(positional_args.pop().value, executing_type, module, var_scopes))
    else:
        if len(positional_args) > len(params):
            loc = ComLoc()
            for arg in args:
                loc = loc.union(arg.loc)
            raise ConversionError(f"`{source_err_rep}` only takes {len(params)} arguments, {len(positional_args)} given").with_loc(loc)

    # parse positional args
    for pix, ast_args in enumerate(positional_args):
        param_bindings[params[pix]] = convert_expr(ast_args.value, executing_type, module, var_scopes)

    # parse keyword args
    for ast_args in keyword_args:
        if ast_args.label is None:
            raise UnreachableError("Keyword param has no label despite earlier check to the contrary")
        param: AbsCtxParam
        for param in params:
            if ast_args.label == param.get_label():
                param = param
                break
        else:
            raise ConversionError(f"Argument of name `{ast_args.label}` is not an parameter of `{source_err_rep}`").with_loc(ast_args.loc)
        if param in param_bindings.keys():
            raise ConversionError(f"Parameter `{param.get_label()}` of `{source_err_rep}` already has a value").with_loc(ast_args.loc)
        param_bindings[param] = convert_expr(ast_args.value, executing_type, module, var_scopes)

    # handle default args
    for ctx_param in params:
        if ctx_param not in param_bindings.keys():
            if not ctx_param.is_defaulted():
                raise ConversionError(f"Parameter `{ctx_param.get_label()}` of `{source_err_rep}` has no value").with_loc(calling_location)
            param_bindings[ctx_param] = None

    return param_bindings, extra_bindings


def convert_func_call(ast_func_call: ExprFuncCall, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxExprNode:
    # Get executor
    ctx_executor = convert_expr(ast_func_call.executor, executing_type, module, var_scopes)
    # If we are building a chain: extend the chain
    if isinstance(ctx_executor, CtxExprPartialChain):
        chain_link = module.get_chain_link(ctx_executor.peek, ast_func_call.func_name, ast_func_call.loc)
        if chain_link is None:
            raise ConversionError(
                f"The chained expression `{ctx_executor.render()}` cannot be continued with function of name `{ast_func_call.func_name}`"
            ).with_loc(ast_func_call.func_name_ident.loc)
        if not chain_link.expects_args:
            raise ConversionError(
                f"The chained expression `{chain_link.render()}` does not expect arguments, cannot invoke it as a function"
            ).with_loc(ast_func_call.func_name_ident.loc)
        arg_bindings, extra_bindings = _build_arg_param_binding(
            list(chain_link.get_ctx_params()), ast_func_call.params, chain_link.allow_extra_args(), chain_link.render(), executing_type, module, var_scopes, ast_func_call.loc
        )
        chain_link.set_chain_data(arg_bindings, extra_bindings)
        return ctx_executor.new_with_link(chain_link, ast_func_call.loc)
    # Otherwise confirm that the executor is an Exec type
    ctx_executor_type = ctx_executor.get_type()
    if not isinstance(ctx_executor_type, ExecType):
        raise ConversionError(f"Cannot run function on non-executing type `{ctx_executor_type.render()}`").with_loc(ctx_executor.loc)

    # Get called function-like structure:
    if (ctx_func := module.get_function(ctx_executor_type, ast_func_call.func_name)) is not None:
        arg_bindings, extra_bindings = _build_arg_param_binding(
            list(ctx_func.get_params()), ast_func_call.params, ctx_func.allow_extra_args(), ctx_func.render(), executing_type, module, var_scopes, ast_func_call.loc
        )

        # Build value-list structures
        param_values: List[CtxExprParamVal] = []
        for ctx_param, binding in arg_bindings.items():
            if binding is not None and (not matches_type(ctx_param.get_param_type(), binding.get_type())):
                raise ConversionError(
                    f"Parameter `{ctx_param.get_label()}` from function of name `{ctx_func.get_name()}` is of type " +
                    f"`{binding.get_type().render()}`, `{ctx_param.get_param_type().render()}` expected"
                ).with_loc(binding.loc)
            bind_loc = binding.loc if binding is not None else ComLoc()
            param_values.append(CtxExprParamVal(ctx_param, binding, src_loc=bind_loc))

        extra_pvals: List[CtxExprExtraParamVal] = []
        if len(extra_bindings) >= 1:
            try:
                extra_arg_type = ctx_func.get_extra_args_type()
            except ContextualisationError:
                raise UnreachableError("Extra binding type does not exist despite extra bindings only containing elements for functions that accept extra args")
            for epix, ebind in enumerate(extra_bindings):
                if not matches_type(extra_arg_type, ebind.get_type()):
                    raise ConversionError(
                        f"Extra argument {epix} of function `{ctx_func.render()}` is of type " +
                        f"`{ebind.get_type().render()}`, `{extra_arg_type.render()}` expected"
                    ).with_loc(ebind.loc)
                extra_pvals.append(CtxExprExtraParamVal(extra_arg_type, ebind, src_loc=ebind.loc))
        # Return function call
        return CtxExprFuncCall(ctx_executor, ctx_func, param_values, extra_pvals, src_loc=ast_func_call.loc)
    elif (chain_link := module.get_chain_link(ctx_executor_type, ast_func_call.func_name, ast_func_call.loc)) is not None:
        if not chain_link.expects_args:
            raise ConversionError(
                f"The chained expression `{chain_link.render()}` does not expect arguments, cannot invoke it as a function"
            ).with_loc(ast_func_call.func_name_ident.loc)
        arg_bindings, extra_bindings = _build_arg_param_binding(
            list(chain_link.get_ctx_params()), ast_func_call.params, chain_link.allow_extra_args(), chain_link.render(), executing_type, module, var_scopes, ast_func_call.loc
        )
        chain_link.set_chain_data(arg_bindings, extra_bindings)
        return CtxExprGenericChain.start(ctx_executor).new_with_link(chain_link, ast_func_call.loc)
    else:
        did_you_mean = module.get_did_you_mean_for_name(ast_func_call.func_name)
        raise ConversionError(
            f"Function of name `{ast_func_call.func_name}` executing on `{ctx_executor_type.render()}` is not defined" +
            (f".  {did_you_mean}" if did_you_mean is not None else "")
        ).with_loc(ast_func_call.func_name_ident.loc)


def convert_property_access(ast_prop_access: ExprPropertyAccess, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxExprNode:
    executor_source: CtxExprNode = convert_expr(ast_prop_access.source, executing_type, module, var_scopes)
    if isinstance(executor_source, CtxExprPartialChain):
        # If we are building a chain: extend the chain
        chain_link = module.get_chain_link(executor_source.peek, ast_prop_access.property_name, ast_prop_access.loc)
        if chain_link is None:
            raise ConversionError(
                f"The chained expression `{executor_source.render()}` cannot be continued with property of name `{ast_prop_access.property_name}`"
            ).with_loc(ast_prop_access.property_name_ident.loc)
        if chain_link.expects_args:
            raise ConversionError(
                f"The chained expression `{chain_link.render()}` expects arguments, cannot invoke it as a property"
            ).with_loc(ast_prop_access.property_name_ident.loc)
        chain_link.set_chain_data(None)
        return executor_source.new_with_link(chain_link, ast_prop_access.loc)

    # Validate the executor & try to find the related property
    exec_type: ComType = executor_source.get_type()
    if isinstance(exec_type, ExecType):
        pass  # Correct
    else:
        raise ConversionError(f"Properties can only be accessed on executable types, not `{exec_type.render()}`").with_loc(executor_source.loc)
    prop = module.get_property(exec_type, ast_prop_access.property_name)

    # If it's not a property maybe it is the start of a chain
    if prop is None:
        chain_link = module.get_chain_link(exec_type, ast_prop_access.property_name, ast_prop_access.loc)
        if chain_link is None:
            raise ConversionError(
                f"Property of name `{ast_prop_access.property_name}` executing on `{exec_type.render()}` is not defined"
            ).with_loc(ast_prop_access.property_name_ident.loc)
        if chain_link.expects_args:
            raise ConversionError(
                f"The chained expression `{chain_link.render()}` expects arguments, cannot invoke it as a property"
            ).with_loc(ast_prop_access.property_name_ident.loc)
        chain_link.set_chain_data(None)
        return CtxExprGenericChain.start(executor_source).new_with_link(chain_link, ast_prop_access.loc)
    return CtxExprPropertyAccess(executor_source, prop, src_loc=ast_prop_access.loc)


def convert_lit_ident(ast_lit_ident: ExprLitIdent, module: CtxModule, var_scopes: List[VarScope]) -> CtxExprVar:
    """Generate a CtxVarExpr from an ast literal identifier"""
    var_name = ast_lit_ident.value
    for vscope in reversed(var_scopes):
        ctx_var = vscope.get_var(var_name)
        if ctx_var is not None:
            break
    else:
        # ctx_var is not a variable in any known scope
        raise ConversionError(f"Variable `{var_name}` is not defined").with_loc(ast_lit_ident.loc)

    if isinstance(ctx_var.var_type, ExecType) and (not var_scopes[-1].var_defined(var_name)):
        # If we found a var of exec type but it was not found in local scope then it may be cleaned up by the time we try and use it
        raise ConversionError(
            f"Executable-typed variable `{var_name}` is accessed from inner scope - It's reference will be deleted by this time. " +
            f"You probably want to select it again again with `world.get_entities().(...).find()`"
        ).with_loc(ast_lit_ident.loc)

    return CtxExprVar(ctx_var, src_loc=ast_lit_ident.loc)
