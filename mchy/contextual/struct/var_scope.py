
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, InertType, StructType
from mchy.errors import ConversionError

if TYPE_CHECKING:
    from mchy.contextual.struct.stmnt import MarkerDeclVar


@dataclass(eq=True)
class CtxVar:
    name: str
    var_type: ComType
    read_only: bool
    declaration_marker: 'MarkerDeclVar'

    def render(self) -> str:
        """Renders in a human readable way"""
        return ("let" if self.read_only else "var") + f" {self.name}: {self.var_type.render()}"


class VarScope:

    def __init__(self) -> None:
        self._vars: Dict[str, CtxVar] = {}

    def var_defined(self, name: str) -> bool:
        return name in self._vars.keys()

    def get_var(self, name: str) -> Optional[CtxVar]:
        if name in self._vars.keys():
            return self._vars[name]
        return None

    def get_var_oerr(self, name: str) -> CtxVar:
        var = self.get_var(name)
        if var is None:
            raise TypeError("Variable unexpectedly doesn't exist")
        return var

    def register_new_var(self, name: str, type: ComType, read_only: bool, declaration_marker: 'MarkerDeclVar', var_loc: ComLoc) -> CtxVar:
        if self.var_defined(name):
            raise ConversionError(f"A Variable of name `{name}` is already defined in this scope").with_loc(var_loc)
        new_var = CtxVar(name, type, read_only, declaration_marker)
        self._vars[name] = new_var
        return new_var
