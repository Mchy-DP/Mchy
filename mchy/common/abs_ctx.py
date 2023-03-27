
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence, Union

from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, TypeUnion, matches_type


class AbsCtxParam(ABC):

    @abstractmethod
    def get_label(self) -> str:
        ...

    @abstractmethod
    def get_param_type(self) -> Union[ComType, TypeUnion]:
        ...

    @abstractmethod
    def is_defaulted(self) -> bool:
        ...

    def render(self) -> str:
        """Renders param in a human readable way"""
        return f"{self.get_label()}: {self.get_param_type().render()}" + (" = ..." if self.is_defaulted() else "")


class AbsCtxFunc(ABC):

    @abstractmethod
    def get_executor(self) -> ExecType:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_params(self) -> Sequence[AbsCtxParam]:
        ...

    @abstractmethod
    def allow_extra_args(self) -> bool:
        ...

    @abstractmethod
    def get_extra_args_type(self) -> Union[TypeUnion, ComType]:
        ...

    @abstractmethod
    def get_param(self, name: str) -> Optional[AbsCtxParam]:
        ...

    @abstractmethod
    def get_return_type(self) -> ComType:
        ...

    def render(self) -> str:
        """Renders function in a human readable way"""
        return (
            f"def " + ((self.get_executor().render()+" ") if self.get_executor().target != ExecCoreTypes.WORLD else "") +
            f"{self.get_name()}({', '.join(param.render() for param in self.get_params())}" +
            (", " if len(self.get_params()) >= 1 else "") +
            (f"*: {self.get_extra_args_type().render()}" if self.allow_extra_args() else "") +
            f") -> {self.get_return_type().render()}"
        )
