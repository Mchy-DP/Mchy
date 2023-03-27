

from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, TypeUnion, matches_type
from mchy.contextual.struct.expr.abs_node import CtxExprLits, CtxExprNode
from mchy.cmd_modules.struct import IField, IStruct
from mchy.errors import ContextualisationError, StatementRepError, UnreachableError


T = TypeVar("T")


def mixed_type_render(type_: Union[type, ComType, TypeUnion]) -> str:
    if isinstance(type_, type):
        return f"<Py {type_.__name__}>"
    return type_.render()


class CtxPyStruct:
    """Unique instance for each IStruct"""

    def __init__(self, istruct: IStruct) -> None:
        self._istruct: IStruct = istruct

    def get_type(self) -> ComType:
        return self._istruct.get_type()

    def get_name(self) -> str:
        return self._istruct.get_name()

    def render(self) -> str:
        return f"{self.get_qualified_name()}(" + ", ".join(f"{field.label}: {mixed_type_render(field.field_type)}" for field in self._istruct.get_fields()) + ")"

    def get_qualified_name(self) -> str:
        return f"{self._istruct.get_namespace().render()}::{self.get_name()}"

    def get_field(self, name: str) -> Optional[IField]:
        for field in self._istruct.get_fields():
            if field.label == name:
                return field
        return None

    def get_fields(self) -> Tuple[IField, ...]:
        return tuple(self._istruct.get_fields())


class CtxPyStructInstance:

    def __init__(self, py_struct: CtxPyStruct, field_binding: Dict[str, Any]):
        self._struct: CtxPyStruct = py_struct
        self._init_field_binding: Dict[str, Any] = field_binding  # Preserved for clone-type operations
        self._fbinding: Dict[IField, Any] = {}
        for fname, fvalue in field_binding.items():
            field = self._struct.get_field(fname)
            if field is None:
                raise ContextualisationError(f"Data supplied for the field `{fname}` however that field does not exist for struct `{self._struct.render()}`")
            if isinstance(field.field_type, (ComType, TypeUnion)):
                if not isinstance(fvalue, CtxExprNode):
                    raise ContextualisationError(
                        f"Data supplied for the field `{fname}` is of type `<Py {type(fvalue).__name__}>`, " +
                        f"<Py `{CtxExprNode.__name__}`> expected.  (field from: {self._struct.render()})"
                    )
                fvalue_type = fvalue.get_type()
                if not matches_type(field.field_type, fvalue_type):
                    raise ContextualisationError(
                        f"Data supplied for the field `{fname}` is of type `{fvalue_type.render()}`, " +
                        f"`{field.field_type.render()}` expected.  (field from: {self._struct.render()})"
                    )
            else:
                if not isinstance(fvalue, field.field_type):
                    raise ContextualisationError(
                        f"Data supplied for the field `{fname}` is of type `<Py {type(fvalue).__name__}>`, " +
                        f"`<Py {field.field_type.__name__}>` expected.  (field from: {self._struct.render()})"
                    )
            self._fbinding[field] = fvalue

    @property
    def struct(self) -> CtxPyStruct:
        return self._struct

    @property
    def fields(self) -> Sequence[IField]:
        return self._struct.get_fields()

    def creation_field_binding(self) -> Dict[str, Any]:
        """Do not access data through here outside of clone-type operations"""
        return self._init_field_binding

    def get_type(self) -> ComType:
        return self._struct.get_type()

    def get_field_data(self, field: IField) -> Any:
        """Will raise KeyError if field does not have attached data"""
        return self._fbinding[field]

    def get_set_fields(self) -> Sequence[IField]:
        return tuple(self._fbinding.keys())

    def get_assert_py_field_data(self, field_name: str, expected_type: Type[T]) -> T:
        field = self.struct.get_field(field_name)
        if field is None:
            raise StatementRepError(f"The field `{field_name}` does not exist in struct `{self.struct.render()}`")
        if not isinstance(field.field_type, type):
            raise StatementRepError(
                f"The field `{field_name}` was requested expecting it to be of type `{mixed_type_render(expected_type)}` " +
                f"however that field is of type `{mixed_type_render(field.field_type)}` in struct `{self.struct.render()}`"
            )
        if not issubclass(expected_type, field.field_type):
            raise StatementRepError(
                f"The field `{field_name}` was requested expecting it to be of type `{mixed_type_render(expected_type)}` " +
                f"however that field is of type `{mixed_type_render(field.field_type)}` in struct `{self.struct.render()}`"
            )
        return self._fbinding[field]

    def get_assert_ctx_field_data(self, field_name: str, expected_type: ComType) -> CtxExprNode:
        field = self.struct.get_field(field_name)
        if field is None:
            raise StatementRepError(f"The field `{field_name}` does not exist in struct `{self.struct.render()}`")
        if not isinstance(field.field_type, (ComType, TypeUnion)):
            raise StatementRepError(
                f"The field `{field_name}` was requested expecting it to be of type `{mixed_type_render(expected_type)}` " +
                f"however that field is of type `{mixed_type_render(field.field_type)}` in struct `{self.struct.render()}`"
            )
        if not matches_type(field.field_type, expected_type):
            raise StatementRepError(
                f"The field `{field_name}` was requested expecting it to be of type `{mixed_type_render(expected_type)}` " +
                f"however that field is of type `{mixed_type_render(field.field_type)}` in struct `{self.struct.render()}`"
            )
        return self._fbinding[field]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CtxPyStructInstance):
            return self._struct == other._struct and self._fbinding == other._fbinding
        return False

    def render(self) -> str:
        return (
            f"{self.struct.get_qualified_name()}(" +
            ", ".join((
                    f"{field.label}: {field.field_type}" + (f" = {field_data}" if (field_data := self._fbinding.get(field)) is not None else "")
                ) for field in self.struct.get_fields()) +
            ")"
        )


class CtxExprPyStruct(CtxExprNode):

    def __init__(self, py_struct: CtxPyStruct, field_binding: Dict[str, Any], **kwargs):
        if "src_loc" not in kwargs:
            kwargs["src_loc"] = ComLoc()
        super().__init__([], **kwargs)
        self.struct_instance = CtxPyStructInstance(py_struct, field_binding)

    def _get_type(self) -> ComType:
        return self.struct_instance.get_type()

    def _flatten_children(self) -> 'CtxExprNode':
        updated_field_binding: Dict[str, Any] = {}
        for field in self.struct_instance.fields:
            try:
                fvalue = self.struct_instance.get_field_data(field)
            except KeyError:
                continue  # Fields with no data don't need to be flattened
            if isinstance(fvalue, CtxExprNode):
                updated_field_binding[field.label] = fvalue.flatten()
            else:
                updated_field_binding[field.label] = fvalue
        return CtxExprPyStruct(self.struct_instance.struct, updated_field_binding, src_loc=self.loc)

    def _flatten_body(self) -> 'CtxExprLits':
        raise UnreachableError(f"Structs cannot be flattened to literal values")

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprPyStruct) and self.struct_instance == other.struct_instance

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(struct=`{self.render()}`)"
        )

    def render(self) -> str:
        return self.struct_instance.render()

    def get_py_field_data(self, field_name: str, expected_type: Type[T]) -> T:
        return self.struct_instance.get_assert_py_field_data(field_name, expected_type)

    def get_mchy_field_data(self, field_name: str, expected_type: ComType) -> CtxExprNode:
        return self.struct_instance.get_assert_ctx_field_data(field_name, expected_type)

    def get_set_fields(self) -> Sequence[IField]:
        return self.struct_instance.get_set_fields()

    def get_set_field_names(self) -> Sequence[str]:
        return [field.label for field in self.struct_instance.get_set_fields()]
