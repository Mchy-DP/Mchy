from typing import Callable, List, Optional, Tuple
from antlr4.error.ErrorStrategy import DefaultErrorStrategy
from antlr4.error.Errors import RecognitionException
from antlr4.CommonTokenFactory import CommonTokenFactory
from antlr4.Token import CommonToken
from mchy.mchy_ast.antlr_typed_help import assert_is_token
from mchy.mchy_ast.mchy_parser import MchyCustomParser


def _create_magic_token(token_factory: CommonTokenFactory, token_type: int, token_text: str, observed_token: CommonToken):
    return token_factory.create(observed_token.source, token_type, token_text, CommonToken.DEFAULT_CHANNEL, -1, -1, observed_token.line, observed_token.column)


class CustomErrorStrategy(DefaultErrorStrategy):

    def __init__(self):
        super().__init__()
        self.__lazy_error_reporting: List[Tuple(RecognitionException, Callable)] = []

    # Simple recovery
    def recoverInline(self, recognizer: MchyCustomParser):
        return super().recoverInline(recognizer)

    # Complex recovery
    def custom_flush_lazy_errs(self, e: Optional[RecognitionException]):
        """Report error until e reached, if e is none flush all errors"""
        while len(self.__lazy_error_reporting) > 0 and ((e is None) or (not self._custom_next_report_is_err(e))):
            # While we have not reached the current error: attempt to report built up errors
            # This ensures error order consistency if a report is attempted without a corresponding flush
            self._custom_raise_next_report()

    def _custom_raise_next_report(self) -> None:
        """Whatever the next lazy report is: raise is as though we never caught it"""
        self.__lazy_error_reporting[0][1]()
        self.__lazy_error_reporting = self.__lazy_error_reporting[1:]

    def _custom_next_report_is_err(self, e: RecognitionException) -> bool:
        """True if the next lazy report is the supplied error"""
        return len(self.__lazy_error_reporting) > 0 and self.__lazy_error_reporting[0][0] == e

    # Complex recovery
    def reportError(self, recognizer: MchyCustomParser, e: RecognitionException):
        """Report or silence errors"""
        super().reportError(recognizer, e)

    def recover(self, recognizer: MchyCustomParser, e: RecognitionException):
        """Attempt to recover from some sort of error"""
        self.custom_flush_lazy_errs(e)
        # Recover here
        if self._custom_next_report_is_err(e):
            self._custom_raise_next_report()
        return super().recover(recognizer, e)
