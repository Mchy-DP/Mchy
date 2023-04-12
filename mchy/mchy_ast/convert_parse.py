from antlr4 import InputStream, CommonTokenStream
from mchy.common.config import Config
from mchy.mchy_ast.error_listener import MchyErrorListener
from mchy.mchy_ast.error_stratagy import CustomErrorStrategy
from mchy.mchy_ast.mchy_lex import MchyCustomLexer
from mchy.mchy_ast.mchy_parser import MchyCustomParser
from mchy.mchy_ast.visitor import AstBuilderVisitor
from mchy.mchy_ast.nodes import Root as ASTRoot


def mchy_parse(file_text: str, config: Config) -> ASTRoot:
    lexer = MchyCustomLexer(InputStream(file_text))
    config.logger.very_verbose("Built Lexer")
    token_stream = CommonTokenStream(lexer)
    config.logger.very_verbose("Built Token Stream")
    mchy_parser = MchyCustomParser(token_stream)
    config.logger.very_verbose("Built parser")
    _strategy = CustomErrorStrategy()
    mchy_parser._errHandler = _strategy
    mchy_parser.removeErrorListeners()
    mchy_parser.addErrorListener(MchyErrorListener(config))
    config.logger.very_verbose("Registered error listeners")
    root: ASTRoot = AstBuilderVisitor().visit(mchy_parser.mchy_file())
    _strategy.custom_flush_lazy_errs(None)  # Ensure no errors are left unreported
    config.logger.very_verbose("AST built")
    return root
