
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple
from mchy.cmd_modules.docs_data import DocsData
from mchy.common.com_loc import ComLoc

from mchy.common.com_types import ComType, ExecType
from mchy.common.config import Config

if TYPE_CHECKING:
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom
    from mchy.cmd_modules.name_spaces import Namespace


class IProp(ABC):

    def get_docs(self) -> DocsData:
        return DocsData()

    @abstractmethod
    def get_namespace(self) -> 'Namespace':
        ...

    @abstractmethod
    def get_executor_type(self) -> ExecType:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_prop_type(self) -> ComType:
        ...

    @abstractmethod
    def stmnt_conv(self, executor: 'SmtAtom', module: 'SmtModule', function: 'SmtFunc', config: Config, loc: ComLoc) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        ...

    def __init_subclass__(cls) -> None:
        new_property = cls()
        new_property.get_namespace().register_new_prop(new_property)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(`{self.render()}`)"

    def render(self) -> str:
        return f"({self.get_executor_type().render()}).{self.get_name()}: {self.get_prop_type()}"
