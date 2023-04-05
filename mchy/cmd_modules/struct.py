
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Sequence, Type, Union
from mchy.cmd_modules.docs_data import DocsData

from mchy.cmd_modules.param import IParam
from mchy.common.com_types import ComType, StructCoreType, StructType, TypeUnion

if TYPE_CHECKING:
    from mchy.cmd_modules.name_spaces import Namespace
    from mchy.contextual.struct.expr import CtxExprNode, CtxExprLits, CtxChainLink
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom


@dataclass(frozen=True)
class IField:
    label: str
    field_type: Union[type, ComType, TypeUnion]  # Can be any python type


class IStruct(ABC):

    __class2type: Dict[Type['IStruct'], StructType] = {}

    @classmethod
    def get_type(cls) -> StructType:
        return IStruct.__class2type[cls]

    def __init__(self) -> None:
        super().__init__()
        IStruct.__class2type[type(self)] = StructType(StructCoreType(self.get_namespace().render(), self.get_name()))

    def get_docs(self) -> DocsData:
        return DocsData()

    @abstractmethod
    def get_namespace(self) -> 'Namespace':
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_fields(self) -> Sequence[IField]:
        ...

    def __init_subclass__(cls) -> None:
        new_struct = cls()
        new_struct.get_namespace().register_new_struct(new_struct)
