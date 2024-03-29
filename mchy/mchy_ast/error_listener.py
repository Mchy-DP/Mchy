from typing import List, Optional, Set
from antlr4 import ParserRuleContext, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from antlr4.Token import CommonToken
from antlr4.error.Errors import RecognitionException, InputMismatchException, NoViableAltException, FailedPredicateException, LexerNoViableAltException
from mchy.common.com_diff import is_similar
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config

from mchy.errors import AbstractTreeError, MchySyntaxError, UnreachableError
from mchy.mchy_ast.antlr_typed_help import assert_is_token, get_expected_toks_str, get_input, get_token_text, loc_end_from_tok
from mchy.mchy_ast.mchy_parser import MchyCustomParser


KEYWORD_TOKENS = [
    MchyCustomParser.VAR, MchyCustomParser.LET, MchyCustomParser.DEF, MchyCustomParser.GROUP, MchyCustomParser.RETURN, MchyCustomParser.WORLD,
    MchyCustomParser.IF, MchyCustomParser.ELIF, MchyCustomParser.ELSE, MchyCustomParser.WHILE, MchyCustomParser.NOT, MchyCustomParser.AND,
    MchyCustomParser.OR, MchyCustomParser.FOR, MchyCustomParser.IN
]

LINE_END_TOKENS = [
    MchyCustomParser.EOF, MchyCustomParser.CBCLOSE, MchyCustomParser.NEWLINE  # CBCLOSE included due to recovery sometimes accepting CBCLOSE as a line ending
]

COMMON_TYPE_STRINGS = [
    "str", "int", "float", "char", "bool", "double", "long", "short", "byte"
]


def _helper_is_typeish(typeish_ident: str) -> bool:
    return any(is_similar(typeish_ident, type_) for type_ in COMMON_TYPE_STRINGS)


def _helper_ctx(recognizer: MchyCustomParser) -> str:
    top: str = ""
    middle: str = ""
    bottom: str = ""
    footer: str = ""
    for i in range(-4, 5):
        token: Optional[CommonToken] = get_input(recognizer).LT(i)
        if token is None:
            continue
        else:
            assert_is_token(token)
        name: str = (recognizer.symbolicNames[token.type] + " ")
        text: str = repr(get_token_text(token))[1:-1]
        length = max(len(name), len(text))
        top += name.ljust(length)
        middle += text.ljust(length)
        if i == 1:
            bottom += "^".ljust(length)
        else:
            bottom += (" " * length)
    footer += ", ".join(recognizer.symbolicNames[etok] for etok in recognizer.getExpectedTokens())
    return "\n".join([top, middle, bottom, footer])


class MchyErrorListener(ErrorListener):

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config

    def syntaxError(self, recognizer: MchyCustomParser, offendingSymbol: CommonToken, line: int, column: int, msg: str, e: Optional[RecognitionException]):
        try:
            return self.__syntaxError(recognizer, offendingSymbol, line, column, msg, e)
        except MchySyntaxError as mchy_err:
            line_end, column_end = loc_end_from_tok(offendingSymbol)
            raise mchy_err.with_loc(ComLoc(line, column, line_end, column_end))

    def __syntaxError(self, recognizer: MchyCustomParser, offendingSymbol: CommonToken, line: int, column: int, msg: str, e: Optional[RecognitionException]):
        # Get error info
        stream: CommonTokenStream = recognizer.getInputStream()
        ctx: ParserRuleContext = recognizer._ctx if recognizer._ctx is not None else None
        parent_ctx: ParserRuleContext = ctx.parentCtx if ctx is not None else None
        expected_toks: Set[int] = set(recognizer.getExpectedTokens())

        # Provide log of backend error info
        self.config.logger.very_verbose(
            f"Mchy Syntax Error: off_sym={recognizer.symbolicNames[offendingSymbol.type]} err={repr(e)} " +
            f"ctx={type(ctx).__name__} parent_ctx={type(parent_ctx).__name__} expected_toks={expected_toks} msg='{msg}'"
        )
        self.config.logger.very_verbose(
            "Further context: \n" + _helper_ctx(recognizer)
        )

        # === Early errors ===
        if offendingSymbol.type == recognizer.UNKNOWN_CHAR:
            raise MchySyntaxError(f"Invalid character {get_token_text(offendingSymbol)} encountered during parsing")
        if isinstance(ctx, (recognizer.Mchy_fileContext)):  # empty file checks
            if ctx.top is None and offendingSymbol.type == recognizer.EOF:
                raise MchySyntaxError(f"Empty file encountered during compilation?")

        # === ctx based errors ===
        if isinstance(ctx, recognizer.Variable_declContext):
            if expected_toks == {recognizer.COLON}:
                raise MchySyntaxError(f"Missing type annotation in declaration of variable `{get_token_text(assert_is_token(ctx.var_name))}`")
        if isinstance(ctx, recognizer.Param_declContext):
            if expected_toks == {recognizer.COLON}:
                param_name: str = get_token_text(assert_is_token(ctx.param_name))
                if offendingSymbol.type == recognizer.IDENTIFIER:
                    if _helper_is_typeish(param_name):
                        raise MchySyntaxError(f"Invalid type annotation, Did you mean `{get_token_text(offendingSymbol)}: {param_name}`?")
                raise MchySyntaxError(f"Missing type annotation in declaration of param `{param_name}`")
        if isinstance(ctx, recognizer.TypeContext):
            if get_input(recognizer).LB(1).type == recognizer.COLON:
                if offendingSymbol.type == recognizer.EQUAL:
                    if isinstance(parent_ctx, recognizer.Variable_declContext):
                        raise MchySyntaxError(f"Missing type in type annotation of the variable declaration of {get_token_text(assert_is_token(parent_ctx.var_name))}")
                if offendingSymbol.type in (recognizer.PCLOSE, recognizer.COMMA):
                    if isinstance(parent_ctx, recognizer.Param_declContext):
                        raise MchySyntaxError(f"Missing type in type annotation of the param declaration of {get_token_text(assert_is_token(parent_ctx.param_name))}")
                raise MchySyntaxError(f"Incomplete type, expected {get_expected_toks_str(recognizer, list(expected_toks))}")
            if get_input(recognizer).LB(1).type == recognizer.GROUP:
                raise MchySyntaxError(f"Incomplete type: Group incomplete, expected {get_expected_toks_str(recognizer, list(expected_toks))}")
            if (offendingSymbol.type == recognizer.WORLD) and ({recognizer.IDENTIFIER} == expected_toks) and (get_input(recognizer).LB(2).type == recognizer.GROUP):
                raise MchySyntaxError(f"Cannot have groups of world")
        if isinstance(ctx, recognizer.ExprContext):
            if (
                        isinstance(parent_ctx, (recognizer.Variable_declContext, recognizer.AssignmentContext)) and
                        (offendingSymbol.type in LINE_END_TOKENS)
                    ):
                raise MchySyntaxError(f"Cannot assign to nothing")
            if isinstance(parent_ctx, recognizer.Return_lnContext):
                if offendingSymbol.type in LINE_END_TOKENS:
                    raise MchySyntaxError(f"Expected expression, got '{repr(get_token_text(offendingSymbol))[1:-1]}' - did you mean `return null`")
                raise MchySyntaxError(f"Expected expression, got '{get_token_text(offendingSymbol)}'")
        if isinstance(ctx, recognizer.Code_blockContext):
            if offendingSymbol.type == recognizer.EOF:
                raise MchySyntaxError("File ended unexpectedly without closing scope - Did you forget a `}`")
            if (
                        isinstance(parent_ctx, (recognizer.If_stmntContext, recognizer.Elif_stmntContext, recognizer.Else_stmntContext)) and
                        (offendingSymbol.type == recognizer.COLON) and {recognizer.CBOPEN} == expected_toks
                    ):
                raise MchySyntaxError("Curly braces { and } should used for scoping, not indentation/colon")
        if isinstance(ctx, recognizer.Function_declContext):
            if (offendingSymbol.type == recognizer.COLON) and ({recognizer.CBOPEN, recognizer.ARROW} == expected_toks):
                raise MchySyntaxError("Curly braces { and } should used for scoping, not indentation/colon")
        if isinstance(ctx, (recognizer.Mchy_fileContext, recognizer.Code_blockContext)):
            if ctx.children is None:
                # Codeblock in process of construction during error
                if offendingSymbol.type == recognizer.CBOPEN:
                    raise MchySyntaxError("Cannot open code block in this context.  Code blocks are only valid after if, while, def, ... - solitary code blocks are not supported.")

                # Generic missing codeblock
                if isinstance(parent_ctx, recognizer.If_stmntContext):
                    raise MchySyntaxError("Missing If-statement body - did you forget to include `{}`?")
                elif isinstance(parent_ctx, recognizer.Elif_stmntContext):
                    raise MchySyntaxError("Missing Elif-statement body - did you forget to include `{}`?")
                elif isinstance(parent_ctx, recognizer.Else_stmntContext):
                    raise MchySyntaxError("Missing Else-statement body - did you forget to include `{}`?")
                else:
                    if isinstance(ctx, recognizer.Code_blockContext):
                        raise MchySyntaxError("Missing code block content - did you forget to include `{}`?")
            else:
                prior_ctx: ParserRuleContext
                if isinstance(ctx, recognizer.Mchy_fileContext):
                    # prior_ctx = File.Top_Scope.Last_elem.scope
                    prior_ctx = ctx.children[0].children[-1].children[0]
                elif isinstance(ctx, recognizer.Code_blockContext):
                    # prior_ctx = Code_block.Last_scope
                    prior_ctx = ctx.children[-1]
                else:
                    raise UnreachableError("Instance of file or code block is neither a file or a code block")

                if isinstance(prior_ctx, recognizer.StmntContext):
                    statement_body = prior_ctx.getChild(0)
                    # Raise more specific error
                    if offendingSymbol.type == recognizer.EQUAL:
                        raise MchySyntaxError(f"Cannot assign to non-variable `{stream.getText(prior_ctx.start.start, offendingSymbol.stop)}`")
                    if offendingSymbol.type == recognizer.SBOPEN:
                        if isinstance(statement_body, recognizer.Variable_declContext):
                            core_type = statement_body.var_type.core_type
                            if core_type is not None:
                                core_type_text = assert_is_token(core_type).text
                                if is_similar(core_type_text, "Group"):
                                    raise MchySyntaxError(
                                        f"Invalid type `{core_type_text}[...` found in declaration of variable " +
                                        f"{assert_is_token(statement_body.var_name).text}, did you mean 'Group[...'?"
                                    )
                elif isinstance(prior_ctx, recognizer.Function_declContext):
                    pass  # Cannot really add more context to this as they can be too varied
                else:
                    raise AbstractTreeError(f"Statement ending encountered outside statement while adding context to error: {msg}")

        # === Specific late errors ===
        if isinstance(ctx, (recognizer.Mchy_fileContext, recognizer.Code_blockContext)):
            # double identifier in a stmnt-expected context
            if offendingSymbol.type == recognizer.IDENTIFIER:
                token_prev = assert_is_token(get_input(recognizer).LT(-1))
                token_this = assert_is_token(get_input(recognizer).LT(1))
                if token_prev.type == recognizer.IDENTIFIER and token_this.type == recognizer.IDENTIFIER:
                    if is_similar(get_token_text(token_prev), "def") or (get_token_text(token_prev) in ("function", "fun", "func")):
                        raise MchySyntaxError(
                            f"No valid option for `{get_token_text(token_prev)} {get_token_text(token_this)}`, did you mean `def {get_token_text(token_this)}`?"
                        )
                    if _helper_is_typeish(get_token_text(token_prev)):
                        raise MchySyntaxError(
                            f"No valid option for `{get_token_text(token_prev)} {get_token_text(token_this)}`, " +
                            f"did you mean `var {get_token_text(token_this)}: {get_token_text(token_prev)}`?"
                        )

        # === Late/slightly less generic errors ===
        if (offendingSymbol.type in KEYWORD_TOKENS) and (recognizer.IDENTIFIER in expected_toks):
            # If the offending token is a keyword and identifier's are valid here then the user probably accidentally misused a keyword
            raise MchySyntaxError(f"The keyword `{get_token_text(offendingSymbol)}` cannot be used in this context")
        if isinstance(ctx, recognizer.ExprContext) and (recognizer.DBQ_STRING in expected_toks):
            # DBQ_STRING is only in expecting_toks if the start of an expression is expected
            raise MchySyntaxError(f"Encountered '{get_token_text(offendingSymbol)}', expected expression")
        if offendingSymbol.type == recognizer.SBOPEN:
            raise MchySyntaxError(f"Cannot use '[' in this context?  Are you attempting to index a list/array, arrays are not yet supported so this won't work.")

        # Super generic catch-all error
        raise MchySyntaxError(msg)
