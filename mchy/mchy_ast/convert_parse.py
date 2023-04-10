from antlr4 import InputStream, CommonTokenStream
from mchy.built.MchyParser import MchyParser
from mchy.common.config import Config
from mchy.mchy_ast.error_listener import MchyErrorListener
from mchy.mchy_ast.mchy_lex import MchyCustomLexer
from mchy.mchy_ast.visitor import AstBuilderVisitor
from mchy.mchy_ast.nodes import Root as ASTRoot


def mchy_parse(file_text: str, config: Config) -> ASTRoot:
    lexer = MchyCustomLexer(InputStream(file_text))
    config.logger.very_verbose("Built Lexer")
    token_stream = CommonTokenStream(lexer)
    config.logger.very_verbose("Built Token Stream")
    mchy_parser = MchyParser(token_stream)
    config.logger.very_verbose("Built parser")
    mchy_parser.removeErrorListeners()
    mchy_parser.addErrorListener(MchyErrorListener(config))
    config.logger.very_verbose("Registered error listeners")
    root: ASTRoot = AstBuilderVisitor().visit(mchy_parser.mchy_file())
    config.logger.very_verbose("AST built")
    return root
