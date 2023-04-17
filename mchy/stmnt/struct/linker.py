
from dataclasses import dataclass
import enum
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple
from mchy.common.com_types import ExecCoreTypes, ExecType, StructType

from mchy.errors import StatementRepError, UnreachableError, VirtualRepError

from mchy.stmnt.struct.function import SmtFunc, SmtMchyFunc
from mchy.stmnt.struct.atoms import SmtVar, SmtPublicVar, SmtPseudoVar
from mchy.stmnt.struct.smt_frag import SmtFragment
from mchy.stmnt.struct.struct import SmtPyStructInstance


@dataclass(frozen=True)
class SmtVarLinkage:
    ns: str
    _store_path: str
    var_name: str
    _public: bool
    _stackless: bool

    def get_store_path(self, stack_level: Optional[int]) -> str:
        if self._stackless:
            return self._store_path
        if stack_level is None:
            raise VirtualRepError(f"Non-Stackless variable `{self.var_name}` has no stack level attached to request for store path. (Scope: `{self._store_path}`)")
        return self._store_path+f".r{stack_level}"+("" if self._public else "I")


@dataclass(frozen=True)
class SmtObjVarLinkage(SmtVarLinkage):
    """Used when the variable stores it's value in an objective rather than in storage - provides access to that objective"""
    _objective: str

    def get_objective(self, stack_level: Optional[int]) -> str:
        if self._stackless:
            return self._objective
        if stack_level is None:
            raise VirtualRepError(f"Non-Stackless variable `{self.var_name}` has no stack level attached to request for objective. (Scope: `{self._objective}`)")
        return self._objective+f"-r{str(stack_level).rjust(3, '0')}"+("" if self._public else "-I")


@dataclass(frozen=True)
class SmtExecVarLinkage(SmtVarLinkage):
    """Used when the variable stores it's value as a tagged entity rather than in storage"""
    _tag: str
    solitary: bool  # True if this is non-grouped
    _player: bool

    def get_full_tag(self, stack_level: Optional[int]) -> str:
        """Get the tag this variable uses, Must not be called on source-variables only targets (as source variables may be `this` which has no tag)"""
        if self._stackless:
            return self._tag+f"-{self.var_name}"
        if stack_level is None:
            raise VirtualRepError(f"Non-Stackless variable `{self.var_name}` has no stack level attached to request for tag. (Scope: `{self._tag}`)")
        return self._tag+f"-r{str(stack_level).rjust(3, '0')}"+("" if self._public else "-I")+f"-{self.var_name}"

    def get_selector(self, stack_level: Optional[int], *, force_group: bool = False) -> str:
        return (
            "@"+('a' if self._player else 'e') +
            f"[tag={self.get_full_tag(stack_level)}" + (
                (', limit=1, sort=arbitrary' if (self.solitary and (not force_group)) else '')
            ) + "]"
        )


class SmtVarFlavour(enum.Enum):
    VAR = enum.auto()
    PARAM = enum.auto()
    RETURN = enum.auto()


class SmtLinker:

    def __init__(self, prj_namespace: str, recursion_limit: int) -> None:
        self._prj_namespace: str = prj_namespace
        self._recursion_limit: int = recursion_limit
        self._func_link: Dict[Tuple[SmtFunc, int], str] = {}
        self._wildcard_func_link: Dict[SmtFunc, str] = {}
        self._var_lookup: Dict[SmtVar, SmtVarLinkage] = {}
        self._int_constants: Set[int] = set()
        self._frag_path_override: Dict[SmtFunc, str] = {}

    def add_const(self, const_value: int) -> None:
        self._int_constants.add(const_value)

    def get_consts(self) -> List[int]:
        return list(self._int_constants)

    def get_const_obj(self) -> str:
        return f"{self._prj_namespace}-mchy_const"

    def add_func(self, func: SmtFunc, ns_loc: str, stack_level: Optional[int]) -> None:
        if stack_level is None:
            self._wildcard_func_link[func] = ns_loc
        else:
            self._func_link[(func, stack_level)] = ns_loc

    def add_frag_path_override(self, func: SmtFunc, ns_loc: str):
        self._frag_path_override[func] = ns_loc

    def lookup_frag(self, func: SmtFunc, stack_level: Optional[int], frag: SmtFragment) -> str:
        frags_path: str
        if func in self._frag_path_override.keys():
            frags_path = self._frag_path_override[func]
        else:
            frags_path = self._lookup_func(func, stack_level) + "fragments"

        return frags_path + "/" + frag.get_frag_name()

    def _lookup_func(self, func: SmtFunc, stack_level: Optional[int]) -> str:
        # If no stack level is provided you must find the file in the wildcard link
        if stack_level is None:
            return self._wildcard_func_link[func]
        # If a stack level is provided but a wildcard entry is present for that function use the wild card option
        if func in self._wildcard_func_link.keys():
            return self._wildcard_func_link[func]
        # Else return the direct stack-respecting link
        return self._func_link[(func, stack_level)]

    def lookup_func(self, func: SmtFunc, stack_level: Optional[int]) -> str:
        if isinstance(func, SmtMchyFunc):
            return self._lookup_func(func, stack_level) + "run"
        else:
            return self._lookup_func(func, stack_level)

    def _get_var_data(self, var: SmtVar, param_var: bool) -> Tuple[str, bool]:
        var_prefix = "param" if param_var else "var"
        if isinstance(var, SmtPublicVar):
            return (f"{var_prefix}_{var.name}", True)
        elif isinstance(var, SmtPseudoVar):
            return (f"{var_prefix}_{var.value}", False)
        else:
            raise UnreachableError("var is neither public nor pseudo - unknown subclass of SmtVar")

    def add_mchy_var(self, var: SmtVar, func: SmtMchyFunc) -> None:
        var_type = SmtVarFlavour.VAR
        if var in func.param_var_lookup.values():
            var_type = SmtVarFlavour.PARAM
        elif var == func.return_var:
            var_type = SmtVarFlavour.RETURN

        self.add_bland_var(var, ["mchy_func", func.get_unique_ident()], stackless=False, var_type=var_type)

    def add_bland_var(self, var: SmtVar, pathing: Sequence[str], *, stackless: bool, var_type: SmtVarFlavour = SmtVarFlavour.VAR):
        if var_type == SmtVarFlavour.VAR:
            var_name, public = self._get_var_data(var, param_var=False)
        elif var_type == SmtVarFlavour.PARAM:
            var_name, public = self._get_var_data(var, param_var=True)
            if not public:
                raise VirtualRepError(f"Non-public parameter encountered for pathing {'.'.join(pathing)}")
        elif var_type == SmtVarFlavour.RETURN:
            var_name = "return"
            public = True
        else:
            raise UnreachableError(f"VarType `{var_type}` is unknown")

        if var in self._var_lookup:
            raise StatementRepError(f"Attempting to add variable that already exists ({var_name})")

        linkage_ns = self._prj_namespace+":mchy"
        storage_path = f"{'.'.join(pathing)}"
        var_com_type = var.get_type()
        if var_com_type.is_intable():
            self._var_lookup[var] = SmtObjVarLinkage(linkage_ns, storage_path, var_name, public, stackless, f"{self._prj_namespace}-{'-'.join(pathing)}")
        elif isinstance(var_com_type, ExecType):
            self._var_lookup[var] = SmtExecVarLinkage(
                linkage_ns, storage_path, var_name, public, stackless, f"{self._prj_namespace}-{'-'.join(pathing)}",
                (not var_com_type.group), (var_com_type.target == ExecCoreTypes.PLAYER)
            )
        else:
            self._var_lookup[var] = SmtVarLinkage(linkage_ns, storage_path, var_name, public, stackless)

    def lookup_var(self, var: SmtVar) -> SmtVarLinkage:
        try:
            return self._var_lookup[var]
        except KeyError as e:
            raise VirtualRepError(f"The variable `{repr(var)}` has no linked name?") from e

    def get_all_sb_objs(self) -> List[str]:
        output_objectives: Set[str] = set()
        for linkage in self._var_lookup.values():
            if isinstance(linkage, SmtObjVarLinkage):
                for stacklevel in range(0, self._recursion_limit):
                    output_objectives.add(linkage.get_objective(stacklevel))
        return sorted(output_objectives)
