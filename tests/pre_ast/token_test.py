from typing import List, Tuple, Union
import pytest

from antlr4 import InputStream, Token
from mchy.mchy_ast.mchy_lex import MchyCustomLexer
from tests.helpers.token_helper import TokRep, compare_tok_reps


def build_tok_stream(math_text: str) -> Tuple[MchyCustomLexer, List[Token]]:
    lexer = MchyCustomLexer(InputStream(math_text))
    token: Token
    return lexer, [token for token in lexer.getAllTokens() if (token.channel == Token.DEFAULT_CHANNEL)]


ML = MchyCustomLexer


@pytest.mark.parametrize("expression, expected_tokens", [
    ("42", [(ML.INT, '42')]),
    ("15+17", [(ML.INT, '15'), ML.PLUS, (ML.INT, '17')]),
    ("15 + \n17", [(ML.INT, '15'), ML.PLUS, ML.NEWLINE, (ML.INT, '17')]),
    ("2+3-5", [(ML.INT, '2'), ML.PLUS, (ML.INT, '3'), ML.MINUS, (ML.INT, '5')]),
])
def test_tree_matches(expression: str, expected_tokens: List[Union[Tuple[int, str], int]]):
    lexer, tokens = build_tok_stream(expression)
    # generate token streams
    expected_tok_reps: List[TokRep] = [(TokRep(token) if isinstance(token, int) else TokRep(token[0], token[1])) for token in expected_tokens]
    observed_token_rep: List[TokRep] = [TokRep(token.type, token.text) for token in tokens]

    equal, comparison_text = compare_tok_reps(observed_token_rep, expected_tok_reps, True)

    assert equal, comparison_text
