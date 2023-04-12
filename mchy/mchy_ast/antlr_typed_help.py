from typing import Any, Optional, Sequence, Tuple, cast

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.Token import CommonToken
from antlr4 import ParserRuleContext

from mchy.common.com_loc import ComLoc
from mchy.errors import AbstractTreeError
from mchy.mchy_ast.mchy_parser import MchyCustomParser


def get_token_text(tok: CommonToken) -> str:
    text: Optional[str] = tok.text  # Any is a mistype it will always be an optional string
    if text is None:
        text = ''
    return text


def assert_is_token(token: Any) -> CommonToken:
    if isinstance(token, CommonToken):
        return token
    else:
        raise AbstractTreeError(f"Token was `{repr(token)}` not token?")


def get_input(recognizer: MchyCustomParser) -> CommonTokenStream:
    return recognizer.getInputStream()


def get_expected_toks_str(recognizer: MchyCustomParser, expected: Sequence[int]) -> str:
    expected_toks = []
    for tok in expected:
        if tok == recognizer.EOF:
            expected_toks.append("<EOF>")
        elif (len(recognizer.literalNames) > tok) and recognizer.literalNames[tok] != "<INVALID>":
            expected_toks.append(recognizer.literalNames[tok])
        elif (len(recognizer.symbolicNames) > tok) and recognizer.symbolicNames[tok] != "<INVALID>":
            expected_toks.append(recognizer.symbolicNames[tok])
        else:
            expected_toks.append("<UNKNOWN_TOKEN>")
    if len(expected_toks) == 0:
        return "<UNKNOWN>"
    elif len(expected_toks) == 1:
        return expected_toks[0]
    else:
        return ", ".join(expected_toks[:-1]) + " or " + expected_toks[-1]


def loc_start_from_tok(tok: CommonToken) -> Tuple[Optional[int], Optional[int]]:
    return tok.line, tok.column


def loc_end_from_tok(tok: CommonToken) -> Tuple[Optional[int], Optional[int]]:
    stop_col: Optional[int] = tok.column
    if (stop_col is not None) and (tok.text is not None):
        # If token has defined end and has text add the length of that text to find the true end
        stop_col += len(tok.text)
    return tok.line, stop_col


def loc_from_tok(tok: CommonToken) -> ComLoc:
    return ComLoc(*loc_start_from_tok(tok), *loc_end_from_tok(tok))


def loc_from_ctx(ctx: ParserRuleContext) -> ComLoc:
    line: Optional[int] = None
    start_col: Optional[int] = None
    stop_col: Optional[int] = None
    stop_line: Optional[int] = None
    if isinstance(ctx.start, CommonToken):
        line, start_col = loc_start_from_tok(ctx.start)
    if isinstance(ctx.stop, CommonToken):
        stop_line, stop_col = loc_end_from_tok(ctx.stop)
    return ComLoc(line, start_col, stop_line, stop_col)
