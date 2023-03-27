

from abc import ABC, abstractmethod
from types import NoneType
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.contextual.struct.expr.structs import CtxPyStructInstance
from mchy.stmnt.struct.struct import SmtPyStructInstance


class SmtAtom(ABC):

    @abstractmethod
    def get_type(self) -> ComType:
        ...


class SmtConstInt(SmtAtom):

    def __init__(self, value: int) -> None:
        self.value: int = value

    def get_type(self) -> ComType:
        return InertType(InertCoreTypes.INT, const=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value})"


class SmtConstStr(SmtAtom):

    def __init__(self, value: str) -> None:
        self.value: str = value

    def get_type(self) -> ComType:
        return InertType(InertCoreTypes.STR, const=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.value}')"


class SmtConstFloat(SmtAtom):

    def __init__(self, value: float) -> None:
        self.value: float = value

    def get_type(self) -> ComType:
        return InertType(InertCoreTypes.FLOAT, const=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value})"


class SmtConstNull(SmtAtom):

    def __init__(self) -> None:
        self.value: None = None  # Provided such that Union[SmtConst*, SmtConstNull].value works

    def get_type(self) -> ComType:
        return InertType(InertCoreTypes.NULL, const=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class SmtWorld(SmtAtom):

    def __init__(self) -> None:
        pass

    def get_type(self) -> ComType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class SmtStruct(SmtAtom):

    def __init__(self, value: SmtPyStructInstance) -> None:
        self.struct_instance: SmtPyStructInstance = value

    def get_type(self) -> ComType:
        return self.struct_instance.get_type()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.struct_instance.render()})"


class SmtVar(SmtAtom):

    @abstractmethod
    def typed_repr(self) -> str:
        ...


class SmtPseudoVar(SmtVar):

    def __init__(self, value: int, var_type: ComType) -> None:
        self.value: int = value
        self._var_type: ComType = var_type

    def get_type(self) -> ComType:
        return self._var_type

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value})"

    def typed_repr(self) -> str:
        return f"{type(self).__name__}({self.value}: {self.get_type().render()})"


class SmtPublicVar(SmtVar):

    def __init__(self, name: str, var_type: ComType) -> None:
        self.name: str = name
        self._var_type: ComType = var_type

    def get_type(self) -> ComType:
        return self._var_type

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.name)})"

    def typed_repr(self) -> str:
        return f"{type(self).__name__}({repr(self.name)}: {self.get_type().render()})"
