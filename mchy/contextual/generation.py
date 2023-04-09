from typing import Dict, Tuple, Union
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_types import StructType, matches_type
from mchy.common.config import Config
from mchy.contextual.expr_generation import convert_expr, convert_expr_noflat, convert_lit_ident
from mchy.contextual.struct.expr import CtxExprLits, CtxExprVar
from mchy.contextual.struct.stmnt import CtxBranch, CtxIfStmnt, CtxReturn, CtxWhileLoop, CtxForLoop
from mchy.mchy_ast.nodes import *
from mchy.contextual.struct import *
from mchy.errors import ContextualisationError, UnreachableError, ConversionError


def convert(ast: Root, config: Config) -> CtxModule:
    if len(ast.children) != 1:
        raise ContextualisationError(f"Malformed AST: Root does not have 1 child ({str(ast)})")
    if isinstance(ast.children[0], Scope):
        ast_scope: Scope = ast.children[0]
    else:
        raise ContextualisationError(f"Malformed AST: Root's child is not a Scope ({str(ast.children[0])})")
    module = CtxModule(config)
    config.logger.very_verbose(f"CTX: Importing standard namespace")
    module.import_ns(Namespace.get_namespace("std"))
    config.logger.very_verbose(f"CTX: Parsing global scope")
    funcs: List[Tuple[FunctionDecl, CtxMchyFunc]] = []
    for stmnt_or_func in ast_scope.children:
        if isinstance(stmnt_or_func, Stmnt):
            if len(stmnt_or_func.children) != 1:
                raise ContextualisationError(f"Malformed AST: Stmnt does not have 1 child ({str(stmnt_or_func)})")
            if isinstance(stmnt_or_func.children[0], ReturnLn):
                raise ConversionError(f"Return cannot be used outside a function").with_loc(stmnt_or_func.children[0].loc)
            module.exec_body.extend(convert_stmnt(stmnt_or_func, None, module, [module.global_var_scope], None, config=config))
        elif isinstance(stmnt_or_func, FunctionDecl):
            config.logger.very_verbose(f"CTX: Parsing function declaration of function with name `{stmnt_or_func.func_name}`")
            func, marker = convert_function_decl(stmnt_or_func, None, module, [module.global_var_scope])
            funcs.append((stmnt_or_func, func))  # Add the function to the list of functions to revisit at the end and build the func-bodies
            config.logger.very_verbose(f"CTX: Registering parsed function")
            func, marker = apply_decorators(func, marker, stmnt_or_func.decorators, module, [module.global_var_scope])
            module.add_function(func)  # Register the function and check for duplicates
            module.exec_body.append(marker)
        else:
            raise ContextualisationError(f"Malformed AST: Non stmnt/func_decl in global scope ({str(stmnt_or_func)})")
    config.logger.very_verbose(f"CTX: Completed global scope conversion")
    config.logger.very_verbose(f"CTX: Converting function bodies")
    for ast_fdec, func in funcs:
        config.logger.very_verbose(f"CTX: Converting function body of function `{func.render()}`")
        # Structure of below enumeration:
        # ast_fdec. body.children[0].children
        #    FDecl.SCOPE.  CODEBLOCK.LIST[STMNT]
        for stmntix, stmnt in enumerate(ast_fdec.body.children[0].children):
            if not isinstance(stmnt, Stmnt):
                raise ContextualisationError(f"Non-statement in body of function `{func.render()}` at statement number `{stmntix}` found `{str(stmnt)}`")
            else:
                func.exec_body.extend(convert_stmnt(stmnt, func.get_executor(), module, [module.global_var_scope, func.func_scope], func, config=config))
    config.logger.very_verbose(f"CTX: AST -> CTX conversion complete!")
    return module


def convert_function_decl(ast_fdecl: FunctionDecl, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> Tuple[CtxMchyFunc, MarkerDeclFunc]:
    exec_type: ComType = convert_explicit_type(ast_fdecl.exec_type, module)
    if isinstance(exec_type, ExecType):
        pass  # Correct
    elif isinstance(exec_type, InertType):
        raise ConversionError(f"Function executor type cannot be inert (int, str, float, etc...)").with_loc(ast_fdecl.exec_type.loc)
    else:
        raise UnreachableError(f"Unhandled CtxType subclass")

    # Parse params and build param default initialization markers
    params: List[CtxMchyParam] = []
    pmarkers: List[MarkerParamDefault] = []
    for param in ast_fdecl.params:
        ptype = convert_explicit_type(param.param_type, module)
        if isinstance(ptype, InertType) and ptype.const:
            raise ConversionError(
                f"Parameter `{param.param_name.value}` of function `{ast_fdecl.func_name}` has compile-constant type `{ptype.render()}`, this is forbidden. " +
                f"Consider using a global OR making runtime type " +
                f"(`{param.param_name.value}: {ptype.render()}` ---> `{param.param_name.value}: {InertType(ptype.target, False, ptype.nullable).render()}`)"
            ).with_loc(param.loc)
        pmarker = (
            MarkerParamDefault(param.param_name.value, None) if param.default_value is None else
            MarkerParamDefault(param.param_name.value, convert_expr(param.default_value, executing_type, module, var_scopes))
        )
        pmarkers.append(pmarker)
        params.append(CtxMchyParam(param.param_name.value, param.param_name.loc, ptype, pmarker))

    # Check for duplicate param labels
    _params_labels = [para.get_label() for para in params]
    for lb in _params_labels:
        if _params_labels.count(lb) > 1:
            raise ConversionError(f"Duplicate argument `{lb}` in function declaration for function of name `{ast_fdecl.func_name}`").with_loc(ast_fdecl.loc)

    fmarker = MarkerDeclFunc(pmarkers)
    func = CtxMchyFunc(exec_type, ast_fdecl.exec_type.loc, ast_fdecl.func_name, params, convert_explicit_type(ast_fdecl.return_type, module), ast_fdecl.return_type.loc, fmarker)
    fmarker.with_func(func)
    return func, fmarker


def _assert_no_params(func: CtxMchyFunc, func_type: str) -> None:
    func_params = list(func.get_params())
    if len(func_params) >= 1:
        raise ConversionError(
            f"{func_type} functions cannot have any parameters.  Consider deleting params: " +
            f"`def {func.get_name()}({func_params[0].render()}{(', ...' if len(func_params) > 1 else '')})` ---> `def {func.get_name()}()`"
        ).with_loc(func_params[0].label_loc)


def apply_decorators(func: CtxMchyFunc, marker: MarkerDeclFunc, decorators: List[Decorator], module: CtxModule, var_scopes: List[VarScope]) -> Tuple[CtxMchyFunc, MarkerDeclFunc]:
    for dec in decorators:
        if dec.dec_name == "ticking":
            if not matches_type(func.get_executor(), ExecType(ExecCoreTypes.WORLD, False)):
                raise ConversionError(
                    f"Ticking functions can only execute as world, not `{func.get_executor().render()}`.  Consider deleting executor type " +
                    f"(`def {func.get_executor().render()} {func.get_name()}...` ---> `def {func.get_name()}...`)"
                ).with_loc(func.executor_loc)
            _assert_no_params(func, "Ticking")
            if not matches_type(InertType(InertCoreTypes.NULL), func.get_return_type()):
                raise ConversionError(
                    f"Ticking functions cannot return anything.  Consider deleting return type: " +
                    f"`def {func.get_name()}() -> {func.get_return_type().render()}{'{'}...{'}'}` ---> `def {func.get_name()}(){'{'}...{'}'}`"
                ).with_loc(func.return_loc)
            module.register_as_ticking(func)
        elif dec.dec_name == "public":
            _assert_no_params(func, "Published")
            module.register_as_public(func)
        else:
            raise ConversionError(
                f"Unknown decorator `{dec.dec_name}`, did you mean 'ticking'?"  # TODO: when decorators are generalized make did you mean more useful
            ).with_loc(dec.decorator_name_ident.loc)
    return func, marker


def convert_stmnt(
            ast_stmnt: Stmnt,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            enc_func: Optional[CtxMchyFunc],
            config: Config
        ) -> List[CtxStmnt]:
    config.logger.very_verbose(f"CTX: Converting statement: `{ast_stmnt.deep_repr()}`")
    if len(ast_stmnt.children) != 1:
        raise ContextualisationError(f"Malformed AST: Stmnt does not have 1 child ({str(ast_stmnt)})")
    stmnt_body: Node = ast_stmnt.children[0]
    if isinstance(stmnt_body, ExprGen):
        return [CtxExprHolder(convert_expr(stmnt_body, executing_type, module, var_scopes))]
    elif isinstance(stmnt_body, WhileLoop):
        return [convert_while_loop(stmnt_body, executing_type, module, var_scopes, enc_func, config)]
    elif isinstance(stmnt_body, ForLoop):
        return convert_for_loop(stmnt_body, executing_type, module, var_scopes, enc_func, config)
    elif isinstance(stmnt_body, IfStruct):
        return [convert_if_struct(stmnt_body, executing_type, module, var_scopes, enc_func, config)]
    elif isinstance(stmnt_body, VariableDecl):
        return [convert_variable_decl(stmnt_body, executing_type, module, var_scopes, enc_func)]
    elif isinstance(stmnt_body, Assignment):
        return [convert_assignment(stmnt_body, executing_type, module, var_scopes)]
    elif isinstance(stmnt_body, ReturnLn):
        return [CtxReturn(convert_expr(stmnt_body.target, executing_type, module, var_scopes))]
    elif isinstance(stmnt_body, UserComment):
        return []  # TODO: Make user comments persist into output to aid user debugging
    elif isinstance(stmnt_body, Scope):
        # TODO: Code is currently dead as codeblocks as statements have been cut from 1.0 release scope -> Reintroduced later
        ctxSCB: CtxScopedCodeBlock = CtxScopedCodeBlock()
        new_scopes: List[VarScope] = list(var_scopes) + [ctxSCB.var_scope]
        for child_stmnt in stmnt_body.stmnts:
            if isinstance(child_stmnt, FunctionDecl):
                raise ContextualisationError(f"Malformed AST: Function declaration unexpectedly found in enclosing scope? {str(stmnt_body)}")
            if not isinstance(child_stmnt, Stmnt):
                raise ContextualisationError(f"Malformed AST: Contents of code block are not statement? ({str(stmnt_body)})")
            ctxSCB.stmnts.extend(convert_stmnt(child_stmnt, executing_type, module, new_scopes, enc_func, config=config))
        return [ctxSCB]
    else:
        raise ContextualisationError(f"Malformed AST: Stmnt body is was of an unexpected node type ({str(stmnt_body)})")


def convert_for_loop(
            ast_for: ForLoop,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            enc_func: Optional[CtxMchyFunc],
            config: Config
        ) -> List[CtxStmnt]:
    var_decl_marker = convert_variable_decl(VariableDecl(False, TypeNode("int"), ast_for.index_var_ident.value, ast_for.lower_bound), executing_type, module, var_scopes, enc_func)
    new_var = convert_lit_ident(ast_for.index_var_ident, module, var_scopes).var
    loop = CtxForLoop(
        new_var,
        ast_for.index_var_ident.loc,
        convert_expr(ast_for.lower_bound, executing_type, module, var_scopes),
        convert_expr(ast_for.upper_bound, executing_type, module, var_scopes),
        []
    )
    for child_stmnt in ast_for.body.children:
        if not isinstance(child_stmnt, Stmnt):
            raise ContextualisationError(f"Malformed AST: Contents of for code block are not statement? ({str(ast_for)})")
        loop.exec_body.extend(convert_stmnt(child_stmnt, executing_type, module, var_scopes, enc_func, config))

    return [var_decl_marker, loop]


def convert_while_loop(
            ast_while: WhileLoop,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            enc_func: Optional[CtxMchyFunc],
            config: Config
        ) -> CtxWhileLoop:
    loop = CtxWhileLoop(convert_expr(ast_while.cond, executing_type, module, var_scopes), [])
    for child_stmnt in ast_while.body.children:
        if not isinstance(child_stmnt, Stmnt):
            raise ContextualisationError(f"Malformed AST: Contents of while code block are not statement? ({str(ast_while)})")
        loop.exec_body.extend(convert_stmnt(child_stmnt, executing_type, module, var_scopes, enc_func, config))
    return loop


def convert_if_struct(
            ast_if_struct: IfStruct,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            enc_func: Optional[CtxMchyFunc],
            config: Config
        ) -> CtxIfStmnt:
    # ### Build branches
    # Build If Branch
    if_branch: CtxBranch = CtxBranch(convert_expr(ast_if_struct.cond, executing_type, module, var_scopes), [])
    for child_stmnt in ast_if_struct.body.children:
        if not isinstance(child_stmnt, Stmnt):
            raise ContextualisationError(f"Malformed AST: Contents of if code block are not statement? ({str(ast_if_struct)})")
        if_branch.exec_body.extend(convert_stmnt(child_stmnt, executing_type, module, var_scopes, enc_func, config))

    # Build Elif Branches
    elif_branches: List[CtxBranch] = []
    cur_elif_node: Optional[ElifStruct] = ast_if_struct.elif_struct
    while cur_elif_node is not None:
        elif_branch: CtxBranch = CtxBranch(convert_expr(cur_elif_node.cond, executing_type, module, var_scopes), [])
        for child_stmnt in cur_elif_node.body.children:
            if not isinstance(child_stmnt, Stmnt):
                raise ContextualisationError(f"Malformed AST: Contents of if code block are not statement? ({str(ast_if_struct)})")
            elif_branch.exec_body.extend(convert_stmnt(child_stmnt, executing_type, module, var_scopes, enc_func, config))
        elif_branches.append(elif_branch)
        cur_elif_node = cur_elif_node.elif_cont

    # Build Else Branch
    else_branch: Optional[CtxBranch] = None
    if ast_if_struct.else_struct is not None:
        else_branch = CtxBranch(CtxExprLitBool(True, src_loc=ast_if_struct.else_struct.loc), [])
        for child_stmnt in ast_if_struct.else_struct.body.children:
            if not isinstance(child_stmnt, Stmnt):
                raise ContextualisationError(f"Malformed AST: Contents of if code block are not statement? ({str(ast_if_struct)})")
            else_branch.exec_body.extend(convert_stmnt(child_stmnt, executing_type, module, var_scopes, enc_func, config))

    # ### Validate branches
    if not matches_type(InertType(InertCoreTypes.BOOL), if_branch.cond.get_type()):
        raise ConversionError(f"If branch condition has type `{if_branch.cond.get_type().render()}`, `bool` expected").with_loc(if_branch.cond.loc)
    for elif_branch in elif_branches:
        if not matches_type(InertType(InertCoreTypes.BOOL), elif_branch.cond.get_type()):
            raise ConversionError(f"Elif branch condition has type `{elif_branch.cond.get_type().render()}`, `bool` expected").with_loc(elif_branch.cond.loc)
    if (else_branch is not None) and ((not isinstance(else_branch.cond, CtxExprLitBool)) or (else_branch.cond.value is not True)):
        raise UnreachableError(f"Else branch condition unexpectedly not True found `{repr(else_branch.cond)}`")

    return CtxIfStmnt(if_branch, elif_branches, else_branch)


def convert_variable_decl(
            ast_var_decl: VariableDecl,
            executing_type: Optional[ExecType],
            module: CtxModule,
            var_scopes: List[VarScope],
            enc_func: Optional[CtxMchyFunc]
        ) -> MarkerDeclVar:
    # Is variable already defined as a variable anywhere?
    if var_scopes[-1].var_defined(ast_var_decl.var_name):
        raise ConversionError(f"Variable of name {ast_var_decl.var_name} is already defined in current scope as {var_scopes[-1].get_var_oerr(ast_var_decl.var_name).render()}")

    # Get var type
    var_ctx_type: ComType = convert_explicit_type(ast_var_decl.var_type, module)

    # Check initial value exists for all variable types that need it
    if ast_var_decl.rhs is None:
        # readonly
        if ast_var_decl.read_only_type:
            raise ConversionError(
                f"Read only (let) variables must be assigned to on declaration " +
                f"(`let {ast_var_decl.var_name}: {var_ctx_type.render()}` -> `let {ast_var_decl.var_name}: {var_ctx_type.render()} = ...`)"
            )
        # const
        if ast_var_decl.var_type.compile_const:
            var_let = "let" if ast_var_decl.read_only_type else "var"
            raise ConversionError(
                f"Compile-time constant variables (type's ending with !) must be assigned to on declaration " +
                f"(`{var_let} {ast_var_decl.var_name}: {var_ctx_type.render()}` -> `{var_let} {ast_var_decl.var_name}: {var_ctx_type.render()} = ...`)"
            )
        # structs
        if isinstance(var_ctx_type, StructType):
            var_let = "let" if ast_var_decl.read_only_type else "var"
            raise ConversionError(
                f"Struct-type variables must be assigned to on declaration " +
                f"(`{var_let} {ast_var_decl.var_name}: {var_ctx_type.render()}` -> `{var_let} {ast_var_decl.var_name}: {var_ctx_type.render()} = ...`)"
            )

    # Create the new variable and marker
    marker = MarkerDeclVar().with_enclosing_function(enc_func)
    new_var = var_scopes[-1].register_new_var(ast_var_decl.var_name, var_ctx_type, ast_var_decl.read_only_type, marker)

    # Add default initialization to the marker
    if ast_var_decl.rhs is None:
        marker.with_default_assignment(None)
    else:
        assign = CtxAssignment(new_var, convert_expr(ast_var_decl.rhs, executing_type, module, var_scopes))
        marker.with_default_assignment(assign)
        _rhs_type = assign.rhs.get_type()
        if ast_var_decl.var_type.compile_const and (not (isinstance(_rhs_type, InertType) and _rhs_type.const)):
            raise ConversionError(f"Compile time constants must be assigned to constant types, not `{_rhs_type.render()}`")
        if ast_var_decl.var_type.compile_const and (not isinstance(assign.rhs, CtxExprLits)):
            raise ContextualisationError(f"Compile time constants must be assigned to literal values - flatten failed to literalize")
    return marker


def convert_assignment(ast_assign: Assignment, executing_type: Optional[ExecType], module: CtxModule, var_scopes: List[VarScope]) -> CtxAssignment:
    lhs_expr = convert_expr_noflat(ast_assign.lhs, executing_type, module, var_scopes)
    rhs_expr = convert_expr(ast_assign.rhs, executing_type, module, var_scopes)
    if isinstance(lhs_expr, CtxExprVar):
        if isinstance(lhs_expr.var.var_type, InertType) and lhs_expr.var.var_type.const:
            raise ConversionError(f"The compile-constant variable `{lhs_expr.var.render()}` cannot be assigned to.  (Attempted: `{lhs_expr.var.name} = {repr(rhs_expr)}`)")
        elif lhs_expr.var.read_only:
            raise ConversionError(f"The read-only variable `{lhs_expr.var.render()}` cannot be assigned to.  (Attempted: `{lhs_expr.var.name} = {repr(rhs_expr)}`)")
        elif isinstance(lhs_expr.var.var_type, StructType):
            raise ConversionError(f"The struct variable `{lhs_expr.var.render()}` cannot be assigned to.  (Attempted: `{lhs_expr.var.name} = {repr(rhs_expr)}`)")
        else:
            return CtxAssignment(lhs_expr.var, rhs_expr)
    raise ConversionError(f"Assignment lhs is not a variable? {repr(lhs_expr)}")  # TODO: render CtxExprNode nicer


def convert_explicit_type(ast_type: TypeNode, module: CtxModule) -> ComType:
    """Converts an ast explicit type TypeNode (such as `int`,`float!` or `Group[Player]`) to the common typing format

    Args:
        ast_type: The AST type-node to convert to the common type format
        module: The module to look for non-builtin types in

    Raises:
        ConversionError: Raised if the type-node is contains a set of features that are incompatible

    Returns:
        ComType: The ComType equivalent to the supplied type-node
    """
    try:
        core_type_enum: CoreTypes = get_type_enum(ast_type.core_type)
    except ConversionError as e:
        # If it's not a built-in maybe it's a library type
        struct = module.get_struct(ast_type.core_type)
        if struct is None:
            raise e
        if ast_type.compile_const:
            fixed_render = ast_type.clone()
            fixed_render.compile_const = False
            raise ConversionError(f"Structs cannot be compile constant.  {ast_type.get_typestr()} -> {fixed_render.get_typestr()}")
        if ast_type.compile_const:
            fixed_render = ast_type.clone()
            fixed_render.compile_const = False
            raise ConversionError(f"Structs cannot be compile constant.  {ast_type.get_typestr()} -> {fixed_render.get_typestr()}")
        if ast_type.nullable:
            fixed_render = ast_type.clone()
            fixed_render.nullable = False
            raise ConversionError(f"Structs cannot be nullable.  {ast_type.get_typestr()} -> {fixed_render.get_typestr()}")
        if ast_type.group:
            raise ConversionError(f"Structs cannot be grouped")
        # There is a struct of that name!
        return struct.get_type()

    if isinstance(core_type_enum, ExecCoreTypes):
        if ast_type.compile_const:
            fixed_render = ast_type.clone()
            fixed_render.compile_const = False
            raise ConversionError(f"Executable types (world, player, etc) cannot be compile-constant.  {ast_type.get_typestr()} -> {fixed_render.get_typestr()}")
        if ast_type.nullable:
            fixed_render = ast_type.clone()
            fixed_render.nullable = False
            raise ConversionError(f"Executable types (world, player, etc) cannot be nullable.  {ast_type.get_typestr()} -> {fixed_render.get_typestr()}")
        if ast_type.group is True and core_type_enum == ExecCoreTypes.WORLD:
            raise ConversionError(f"Cannot have a group of world")
        return ExecType(core_type_enum, ast_type.group)
    elif isinstance(core_type_enum, InertCoreTypes):
        if ast_type.group:
            raise ConversionError(f"Cannot have groups of inert types (bool, int, float, str, etc)")
        if core_type_enum == InertCoreTypes.NULL and ast_type.nullable:
            raise ConversionError(f"Null is innately nullable, `?` is redundant (`null?` -> `null`)")
        return InertType(core_type_enum, ast_type.compile_const, ast_type.nullable)
    else:
        raise UnreachableError("Unhandled return type")


def get_type_enum(type_string: str) -> CoreTypes:
    if type_string == "null":
        return InertCoreTypes.NULL
    if type_string == "bool":
        return InertCoreTypes.BOOL
    elif type_string == "int":
        return InertCoreTypes.INT
    elif type_string == "float":
        return InertCoreTypes.FLOAT
    elif type_string == "str":
        return InertCoreTypes.STR
    elif type_string == "world":
        return ExecCoreTypes.WORLD
    elif type_string == "Entity":
        return ExecCoreTypes.ENTITY
    elif type_string == "Player":
        return ExecCoreTypes.PLAYER
    else:
        lower_valid: Dict[str, str] = {ts.lower(): ts for ts in VALID_TYPE_STRINGS}
        if type_string.lower() in lower_valid.keys():
            # Added to hopefully easy the transition to mchy from other languages with different standards for type capitalization
            raise ConversionError(f"Core type `{type_string}` is not known, did you mean `{lower_valid[type_string.lower()]}`")
        else:
            raise ConversionError(f"Core type `{type_string}` is not known")
