from typing import Dict, List, Tuple, Type, TypeVar
from mchy.cmd_modules.chains import IChainLink
from mchy.contextual.struct import InertType
from mchy.common.com_types import ComType, ExecType, InertCoreTypes
from mchy.errors import StatementRepError, VirtualRepError
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstFloat, SmtConstInt, SmtStruct, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker
from mchy.stmnt.struct.struct import SmtPyStructInstance
from mchy.stmnt.helpers import smt_get_exec_vdat

NULL_CTX_TYPE = InertType(InertCoreTypes.NULL)

T = TypeVar("T", bound=SmtAtom)
L = TypeVar("L", bound=IChainLink)


def get_key_with_type(binding: Dict[str, SmtAtom], key: str, atom_type: Type[T]) -> T:
    # get value
    if key not in binding.keys():
        raise StatementRepError(f"Parameter of name `{key}` is missing from bound parameters")
    value = binding[key]
    # handle upcast int->float
    if issubclass(atom_type, SmtConstFloat) and isinstance(value, SmtConstInt):
        value = SmtConstFloat(float(value.value))
    # return value
    if isinstance(value, atom_type):
        return value
    else:
        raise StatementRepError(f"Parameter of name `{key}` is of type `{type(value).__name__}`, `{atom_type.__name__}` expected")


def get_struct_instance(location_atom: SmtAtom) -> SmtPyStructInstance:
    if isinstance(location_atom, SmtStruct):
        return location_atom.struct_instance
    else:
        raise VirtualRepError(f"Location atom is not a literal struct, found {repr(location_atom)}")


def get_exec_vdat(executor: SmtAtom, linker: SmtLinker) -> SmtExecVarLinkage:
    return smt_get_exec_vdat(executor, linker)


def get_links_of_type(
            clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]], link_type: Type[L]
        ) -> List[Tuple[L, Dict[str, 'SmtAtom'], List['SmtAtom']]]:
    matches: List[Tuple[L, Dict[str, 'SmtAtom'], List['SmtAtom']]] = []
    for link, pbinding, extra in clink_param_binding:
        if isinstance(link, link_type):
            matches.append((link, pbinding, extra))
    return matches


def get_link_of_type(clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]], link_type: Type[L]) -> Tuple[L, Dict[str, 'SmtAtom'], List['SmtAtom']]:
    matches = get_links_of_type(clink_param_binding, link_type)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise StatementRepError(f"No link of type {link_type.__name__} in param binding: {repr(clink_param_binding)}")
    else:
        raise StatementRepError(f"Multiple matches of type {link_type.__name__} in param binding: {repr(clink_param_binding)}")
