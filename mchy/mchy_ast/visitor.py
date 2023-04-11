import antlr4
from mchy.built.MchyVisitor import MchyVisitor
from mchy.errors import UnreachableError
from mchy.mchy_ast.antlr_typed_help import loc_from_ctx, loc_from_tok
from mchy.mchy_ast.mchy_parser import MchyCustomParser
from mchy.mchy_ast.nodes import *


class AstBuilderVisitor(MchyVisitor):

    def visitMchy_file(self, ctx: MchyCustomParser.Mchy_fileContext):
        return self.visit(ctx.top)

    def visitTop_level_scope(self, ctx: MchyCustomParser.Top_level_scopeContext):
        return Root(Scope(*list(self.visit(child) for child in ctx.children)))

    def visitStmnt(self, ctx: MchyCustomParser.StmntContext):
        stmnt_child: Node = self.visit(ctx.children[0])
        return Stmnt(stmnt_child).with_loc(loc_from_ctx(ctx).with_line_end(stmnt_child.loc.line_end).with_col_end(stmnt_child.loc.col_end))

    def visitFunction_decl(self, ctx: MchyCustomParser.Function_declContext):
        return_type: TypeNode
        if ctx.return_type is None:
            return_type = TypeNode("null")
        else:
            return_type = self.visit(ctx.return_type)
        exec_type: TypeNode
        if ctx.exec_type is None:
            exec_type = TypeNode("world")
        else:
            exec_type = self.visit(ctx.exec_type)
        return FunctionDecl(
            str(ctx.func_name.text), exec_type, return_type, self.visit(ctx.body), self.visit(ctx.decorators),
            *(self.visit(ctx.params) if ctx.params is not None else [])
        ).with_loc(loc_from_ctx(ctx))

    def visitDecorator_list(self, ctx: MchyCustomParser.Decorator_listContext):
        if isinstance(ctx.children, list):
            return [self.visit(child) for child in ctx.children[::2]]  # [::2] to skip the Newlines
        else:
            return []

    def visitDecorator(self, ctx: MchyCustomParser.DecoratorContext):
        return Decorator(ExprLitIdent(ctx.decorator_name.text).with_loc(loc_from_tok(ctx.decorator_name))).with_loc(loc_from_ctx(ctx))

    def visitRaw_cmd(self, ctx: MchyCustomParser.Raw_cmdContext):
        return ExprFuncCall(
            ExprLitWorld(None).with_loc(ComLoc()),  # No location provided as it would be meaningless
            ExprLitIdent("cmd"),
            ExprFragParam(label=ExprLitIdent("mc_cmd"), value=ExprLitStr(ctx.mc_cmd.text.lstrip("\t ")))
        )

    def visitWhile_loop(self, ctx: MchyCustomParser.While_loopContext):
        return WhileLoop(self.visit(ctx.condition), self.visit(ctx.body)).with_loc(loc_from_ctx(ctx))

    def visitFor_loop(self, ctx: MchyCustomParser.For_loopContext):
        return ForLoop(
            ExprLitIdent(ctx.index_var_name.text).with_loc(loc_from_tok(ctx.index_var_name)),
            self.visit(ctx.lower_bound),
            self.visit(ctx.upper_bound),
            self.visit(ctx.body)
        ).with_loc(loc_from_ctx(ctx))

    def visitFor_range_bound(self, ctx: MchyCustomParser.For_range_boundContext):
        if len(ctx.children) == 1:
            bound = ctx.children[0].symbol
            if bound.type == MchyCustomParser.IDENTIFIER:
                return ExprLitIdent(str(bound.text)).with_loc(loc_from_tok(bound))
            elif bound.type == MchyCustomParser.INT:
                return ExprLitInt(int(bound.text)).with_loc(loc_from_tok(bound))
            else:
                raise TypeError(f"Non-bracketed expression in for loop bound is not int or variable, found `{bound.type}`")
        else:  # '(' expr ')'
            return self.visit(ctx.children[1])

    def visitIf_stmnt(self, ctx: MchyCustomParser.If_stmntContext):
        return IfStruct(
            self.visit(ctx.condition),
            self.visit(ctx.body),
            self.visit(ctx.elif_comp) if ctx.elif_comp is not None else None,
            self.visit(ctx.else_comp) if ctx.else_comp is not None else None
        ).with_loc(loc_from_ctx(ctx))

    def visitElif_stmnt(self, ctx: MchyCustomParser.Elif_stmntContext):
        return ElifStruct(self.visit(ctx.condition), self.visit(ctx.body), self.visit(ctx.continuation) if ctx.continuation is not None else None).with_loc(loc_from_ctx(ctx))

    def visitElse_stmnt(self, ctx: MchyCustomParser.Else_stmntContext):
        return ElseStruct(self.visit(ctx.body)).with_loc(loc_from_ctx(ctx))

    def visitScoped_code_block(self, ctx: MchyCustomParser.Scoped_code_blockContext):
        code_block: CodeBlock = self.visit(ctx.block)
        return Scope(code_block).with_loc(code_block.loc)

    def visitCode_block(self, ctx: MchyCustomParser.Code_blockContext):
        filtered_stmnts = []
        for stmnt in ctx.children[1:]:
            if isinstance(stmnt, antlr4.TerminalNode):
                if stmnt.symbol.type in (MchyCustomParser.CBCLOSE, MchyCustomParser.CBOPEN, MchyCustomParser.NEWLINE):
                    continue
            else:
                filtered_stmnts.append(stmnt)
        return CodeBlock(*list(self.visit(child) for child in filtered_stmnts)).with_loc(loc_from_ctx(ctx))

    def visitVariable_decl(self, ctx: MchyCustomParser.Variable_declContext):
        read_only: bool
        if ctx.varkw.type == MchyCustomParser.VAR:
            read_only = False
        elif ctx.varkw.type == MchyCustomParser.LET:
            read_only = True
        else:
            raise TypeError(f"variable declaration keyword is neither `var` nor `const`? (found: {MchyCustomParser.symbolicNames[ctx.varkw.type]})")
        return VariableDecl(
            read_only,
            self.visit(ctx.var_type),
            ExprLitIdent(ctx.var_name.text).with_loc(loc_from_tok(ctx.var_name)),
            (self.visit(ctx.assignment_target) if ctx.assignment_target is not None else None)
        ).with_loc(loc_from_ctx(ctx))

    def visitAssignment(self, ctx: MchyCustomParser.AssignmentContext):
        return Assignment(
            ExprLitIdent(str(ctx.lhs.text)).with_loc(loc_from_tok(ctx.lhs)),
            self.visit(ctx.rhs)
        ).with_loc(loc_from_ctx(ctx))

    def visitReturn_ln(self, ctx: MchyCustomParser.Return_lnContext):
        return ReturnLn(self.visit(ctx.target)).with_loc(loc_from_ctx(ctx))

    def visitUser_comment(self, ctx: MchyCustomParser.User_commentContext):
        return UserComment(ctx.com_tok.text).with_loc(loc_from_ctx(ctx))

    def visitType(self, ctx: MchyCustomParser.TypeContext):
        core_type: str
        if ctx.core_type is None and ctx.group_target is None:
            # Should be un-raisable if the parser does it's job
            raise TypeError(f"type-node has no target")
        elif ctx.core_type is not None and ctx.group_target is not None:
            # Should be un-raisable if the parser does it's job
            raise TypeError(f"type-node has 2 targets, both group & core_type exist (`{ctx.core_type}` vs `{ctx.group_target}`)")
        elif ctx.core_type is not None:
            core_type = str(ctx.core_type.text)
        elif ctx.group_target is not None:
            core_type = str(ctx.group_target.text)
        else:
            # how did we even get here
            raise UnreachableError()
        return TypeNode(core_type, group=(ctx.groupkw is not None), compile_const=(ctx.constant is not None), nullable=(ctx.nullable is not None)).with_loc(loc_from_ctx(ctx))

    def visitExprParen(self, ctx: MchyCustomParser.ExprParenContext):
        return self.visit(ctx.contents)

    def visitExprFuncCall(self, ctx: MchyCustomParser.ExprFuncCallContext):
        return ExprFuncCall(
            self.visit(ctx.executor),
            ExprLitIdent(str(ctx.func_name.text)).with_loc(loc_from_tok(ctx.func_name)),
            *(self.visit(ctx.params) if ctx.params is not None else [])
        ).with_loc(loc_from_ctx(ctx))

    def visitExprWorldFuncCall(self, ctx: MchyCustomParser.ExprWorldFuncCallContext):
        return ExprFuncCall(
            ExprLitWorld(None),
            ExprLitIdent(str(ctx.func_name.text)).with_loc(loc_from_tok(ctx.func_name)),
            *(self.visit(ctx.params) if ctx.params is not None else [])
        ).with_loc(loc_from_ctx(ctx))

    def visitParam_list(self, ctx: MchyCustomParser.Param_listContext):
        # The odd numbered children are comma's and so are skipped
        return [self.visit(child) for child in ctx.children[::2]]

    def visitParam(self, ctx: MchyCustomParser.ParamContext):
        return ExprFragParam(
            value=self.visit(ctx.value),
            label=(ExprLitIdent(str(ctx.label.text)).with_loc(loc_from_tok(ctx.label)) if ctx.label is not None else None)
        ).with_loc(loc_from_ctx(ctx))

    def visitParam_decl_list(self, ctx: MchyCustomParser.Param_decl_listContext):
        # The odd numbered children are comma's and so are skipped
        return [self.visit(child) for child in ctx.children[::2]]

    def visitParam_decl(self, ctx: MchyCustomParser.Param_declContext):
        return ParamDecl(
            ExprLitIdent(str(ctx.param_name.text)).with_loc(loc_from_tok(ctx.param_name)),
            self.visit(ctx.param_type),
            (self.visit(ctx.default_value) if ctx.default_value is not None else None)
        ).with_loc(loc_from_ctx(ctx))

    def visitExprPropertyAccess(self, ctx: MchyCustomParser.ExprPropertyAccessContext):
        return ExprPropertyAccess(self.visit(ctx.source), ExprLitIdent(str(ctx.attribute.text)).with_loc(loc_from_tok(ctx.attribute))).with_loc(loc_from_ctx(ctx))

    def visitExprExponent(self, ctx: MchyCustomParser.ExprExponentContext):
        return ExprExponent(self.visit(ctx.base), self.visit(ctx.exponent)).with_loc(loc_from_ctx(ctx))

    def visitExprUnaryMinus(self, ctx: MchyCustomParser.ExprUnaryMinusContext):
        return ExprMinus(ExprLitInt(0), self.visit(ctx.target)).with_loc(loc_from_ctx(ctx))

    def visitExprMultDivMod(self, ctx: MchyCustomParser.ExprMultDivModContext):
        if ctx.sign.text == "*":
            return ExprMult(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.sign.text == "/":
            return ExprDiv(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.sign.text == "%":
            return ExprMod(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        else:
            raise TypeError(f"Unknown mult-div case, {ctx.sign.text=}")

    def visitExprPlusMinus(self, ctx: MchyCustomParser.ExprPlusMinusContext):
        if ctx.sign.text == "+":
            return ExprPlus(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.sign.text == "-":
            return ExprMinus(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        else:
            raise TypeError(f"Unknown plus-minus case, {ctx.sign.text=}")

    def visitExprRelation(self, ctx: MchyCustomParser.ExprRelationContext):
        if not isinstance(ctx.comparison, antlr4.Token):
            raise TypeError(f"Expression relation's comparison is not a token, got: {str(ctx.comparison)} ({repr(ctx.comparison)})")
        if ctx.comparison.type == MchyCustomParser.EQUALITY:
            return ExprEquality(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.comparison.type == MchyCustomParser.INEQUALITY:
            return ExprInequality(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.comparison.type == MchyCustomParser.COMP_GTE:
            return ExprCompGTE(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.comparison.type == MchyCustomParser.COMP_GT:
            return ExprCompGT(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.comparison.type == MchyCustomParser.COMP_LTE:
            return ExprCompLTE(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        elif ctx.comparison.type == MchyCustomParser.COMP_LT:
            return ExprCompLT(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))
        else:
            raise TypeError(f"Unknown Relation comparison, {ctx.comparison} ({repr(ctx.comparison)})")

    def visitExprNot(self, ctx: MchyCustomParser.ExprNotContext):
        return ExprNot(self.visit(ctx.target)).with_loc(loc_from_ctx(ctx))

    def visitExprAnd(self, ctx: MchyCustomParser.ExprAndContext):
        return ExprAnd(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))

    def visitExprOr(self, ctx: MchyCustomParser.ExprOrContext):
        return ExprOr(self.visit(ctx.left), self.visit(ctx.right)).with_loc(loc_from_ctx(ctx))

    def visitExprNullCoalescing(self, ctx: MchyCustomParser.ExprNullCoalescingContext):
        return ExprNullCoal(self.visit(ctx.opt_expr), self.visit(ctx.default_expr)).with_loc(loc_from_ctx(ctx))

    def visitLiteralIdent(self, ctx: MchyCustomParser.LiteralIdentContext):
        return ExprLitIdent(str(ctx.value.text)).with_loc(loc_from_ctx(ctx))

    def visitLiteralFloat(self, ctx: MchyCustomParser.LiteralFloatContext):
        return ExprLitFloat(float(ctx.value.text)).with_loc(loc_from_ctx(ctx))

    def visitLiteralInt(self, ctx: MchyCustomParser.LiteralIntContext):
        return ExprLitInt(int(ctx.value.text)).with_loc(loc_from_ctx(ctx))

    def visitLiteralStrDBQ(self, ctx: MchyCustomParser.LiteralStrDBQContext):
        return ExprLitStr(str(ctx.value.text)[1:-1].replace('\\"', '"')).with_loc(loc_from_ctx(ctx))

    def visitLiteralStrSGQ(self, ctx: MchyCustomParser.LiteralStrSGQContext):
        return ExprLitStr(str(ctx.value.text)[1:-1].replace("\\'", "'")).with_loc(loc_from_ctx(ctx))

    def visitLiteralNull(self, ctx: MchyCustomParser.LiteralNullContext):
        return ExprLitNull(None).with_loc(loc_from_ctx(ctx))

    def visitLiteralWorld(self, ctx: MchyCustomParser.LiteralWorldContext):
        return ExprLitWorld(None).with_loc(loc_from_ctx(ctx))

    def visitLiteralThis(self, ctx: MchyCustomParser.LiteralThisContext):
        return ExprLitThis(None).with_loc(loc_from_ctx(ctx))

    def visitLiteralTrue(self, ctx: MchyCustomParser.LiteralTrueContext):
        return ExprLitBool(True).with_loc(loc_from_ctx(ctx))

    def visitLiteralFalse(self, ctx: MchyCustomParser.LiteralFalseContext):
        return ExprLitBool(False).with_loc(loc_from_ctx(ctx))
