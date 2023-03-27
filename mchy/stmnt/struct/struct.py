

import enum
from typing import Any, Dict, Literal, Type, TypeVar, Union

from mchy.common.com_types import ComType, StructType
from mchy.errors import StatementRepError, VirtualRepError


T = TypeVar("T")


class SmtPyStructInstance:

    class StructSpecialTok(enum.Enum):
        NIL = enum.auto()
    NIL = StructSpecialTok.NIL

    def __init__(self, struct_type: ComType, field_binding: Dict[str, Any]) -> None:
        if not isinstance(struct_type, StructType):
            raise StatementRepError(f"Struct of non-struct type `{repr(struct_type)}`?")
        self.struct_type: StructType = struct_type
        self.field_binding: Dict[str, Any] = field_binding  # TypeChecking done by this point so we just assume it's right

    def get_type(self) -> StructType:
        return self.struct_type

    def render(self) -> str:
        return f"Struct<{self.struct_type.target.name}>({', '.join(f'{fname} = {fvalue}' for fname, fvalue in self.field_binding.items())})"

    def get_asserting_type(self, key: str, expected_type: Type[T]) -> T:  # may raise keyerror if field not set
        if isinstance(self.field_binding[key], expected_type):
            return self.field_binding[key]  # type: ignore  # False positive
        else:
            raise VirtualRepError(f"field {key} was not of expected type {expected_type}?")

    def get_asserting_type_or_NIL(self, key: str, expected_type: Type[T]) -> Union[T, Literal[StructSpecialTok.NIL]]:
        try:
            return self.get_asserting_type(key, expected_type)
        except KeyError:
            return SmtPyStructInstance.StructSpecialTok.NIL
