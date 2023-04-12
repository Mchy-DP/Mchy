import enum
from typing import Any, Dict, Literal, Optional, Tuple, TypeVar, Union

from mchy.common.com_loc import ComLoc


T = TypeVar("T", bound='ConversionError')


class UnreachableError(Exception):
    pass


class ConversionError(Exception):
    """An error during conversion, This generally should be caught and context added and usually indicates an error in user code"""

    class InterceptFlags(enum.Enum):  # Each flag indicates a specific place that this error need to to be intercepted and processed in a higher scope, failure to intercept is bad
        PARTIAL_CHAIN_OPTIONS = enum.auto()  # used to indicate 'did you mean' should be added for chain completions
        LIBRARY_LOCLESS = enum.auto()  # used to indicate this error expects to be given a location as it is a library error and so the init site couldn't add one

    def __init__(self, message: str, _prefix: Optional[str] = None, _loc: ComLoc = ComLoc()):
        super().__init__(message)
        self._msg: str = message
        self._prefix: Optional[str] = _prefix
        self._loc: ComLoc = _loc
        self.intercept_flags: Dict[ConversionError.InterceptFlags, Any] = {}

    def with_loc(self: T, src_loc: ComLoc) -> T:
        self._loc = src_loc
        return self

    def with_intercept(self, flag: InterceptFlags, data: Any = None):
        self.intercept_flags[flag] = data
        return self

    def intercept(self, flag: InterceptFlags) -> Union[Literal[False], Tuple[Any]]:
        if flag in self.intercept_flags.keys():
            return (self.intercept_flags.pop(flag), )  # Return result as a tuple of one to ensure it is truthy
        return False

    def msg(self) -> str:
        msg: str = ""
        if self._prefix is not None:
            msg += f"{self._prefix}: "
        if self._loc.line is not None:
            msg += f"Line {self._loc.line}"
            if self._loc.col_start is not None:
                msg += f":{self._loc.col_start}"
            msg += "; "
        msg += self._msg
        return msg

    def __repr__(self) -> str:
        return (super().__repr__()[:-1] + f", loc={self._loc.render()})")

    def append_to_msg(self, extra_info: str) -> None:
        self.args = (self.args[0]+extra_info,)
        self._msg = self._msg+extra_info

    @property
    def loc(self) -> ComLoc:
        return self._loc


class LibConversionError(ConversionError):

    def __init__(self, message: str, _prefix: Optional[str] = None, _loc: ComLoc = ComLoc()):
        super().__init__(message, _prefix, _loc)
        self.with_intercept(ConversionError.InterceptFlags.LIBRARY_LOCLESS)


class MchySyntaxError(ConversionError):
    """An error in your syntax prevented continued compilation, This indicates an error in user code"""

    def __init__(self, message: str):
        super().__init__(message, "Syntax Error")


class AbstractTreeError(Exception):
    """An error in the generation of the AST layer -> this generally should not be caught and indicates a mistake in mchy not in user code"""


class ContextualisationError(Exception):
    """An error in the generation of the contextual layer -> this generally should not be caught and indicates a mistake in mchy not in user code"""


class StatementRepError(Exception):
    """An error in the representation of the CST as a sequence of statements -> this generally should not be caught and indicates a mistake in mchy not in user code"""


class VirtualRepError(Exception):
    """An error in the generation of the virtual datapack from the code statements -> this generally should not be caught and indicates a mistake in mchy not in user code"""
