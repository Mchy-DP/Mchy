

from typing import Dict, List, Tuple
from mchy.common.com_types import ComType, ExecType
from mchy.contextual.struct.ctx_func import CtxMchyFunc, CtxMchyParam
from mchy.errors import StatementRepError

from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtPseudoVar, SmtPublicVar, SmtVar
from mchy.stmnt.struct.smt_frag import RoutingFlavour, SmtFragment


class SmtFunc:

    def __init__(self) -> None:
        self._pseudo_index: int = 0
        self._pseudo_vars: Dict[int, SmtPseudoVar] = {}
        self._public_vars: Dict[str, SmtPublicVar] = {}
        self._fragments: List[SmtFragment] = []
        self._func_frag: SmtFragment = SmtFragment(lambda x: self._fragments.append(x), [])
        self._fragments = []

        fid = hex(abs(hash(str(id(self)))) % (16**8))[2:]  # abs-hash-str makes the fid very different for similar values out of id
        self._id = f"{fid[:4]}-{fid[4:]}".upper()

    @property
    def id(self):
        return self._id

    def new_pseudo_var(self, var_type: ComType) -> SmtPseudoVar:
        new_var = SmtPseudoVar(self._pseudo_index, var_type)
        self._pseudo_vars[self._pseudo_index] = new_var
        self._pseudo_index += 1
        return new_var

    def new_public_var(self, name: str, var_type: ComType) -> SmtPublicVar:
        try:
            return self._public_vars[name]
        except KeyError:
            new_var = SmtPublicVar(name, var_type)
            self._public_vars[name] = new_var
            return new_var

    def get_public_vars(self) -> Tuple[SmtPublicVar, ...]:
        return tuple(self._public_vars.values())

    def get_pseudo_vars(self) -> Tuple[SmtPseudoVar, ...]:
        return tuple(self._pseudo_vars.values())

    def get_all_vars(self) -> Tuple[SmtVar, ...]:
        return self.get_public_vars() + self.get_pseudo_vars()

    @property
    def func_frag(self) -> SmtFragment:
        return self._func_frag

    @property
    def fragments(self) -> List[SmtFragment]:
        """Get function fragments (excluding entrypoint/func_frag fragment)"""
        return self._fragments


class SmtGhostFunc(SmtFunc):

    def new_public_var(self, name: str, var_type: ComType) -> SmtPublicVar:
        raise StatementRepError(f"Imported function attempted to request a public variable (requested var of name `{name}` with type `{var_type.render()}`)")


class SmtMchyFunc(SmtFunc):

    def __init__(self, enclosing_func: SmtFunc, mchy_func: CtxMchyFunc) -> None:
        super().__init__()
        self._mchy_func: CtxMchyFunc = mchy_func
        self.param_var_lookup: Dict[str, SmtPublicVar] = {}
        for param in mchy_func.get_params():
            self.param_var_lookup[param.get_label()] = self.new_public_var(param.get_label(), param.get_param_type())
        self.return_var: SmtPseudoVar = self.new_pseudo_var(mchy_func.get_return_type())
        self.executor_var: SmtPseudoVar = self.new_pseudo_var(mchy_func.get_executor())
        self.param_default_lookup: Dict[str, SmtPseudoVar] = {}

    def get_func_name(self) -> str:
        return self._mchy_func.get_name()

    def get_executor_type(self) -> ExecType:
        return self._mchy_func.get_executor()

    def get_unique_ident(self) -> str:
        return self.get_func_name() + "_" + str(self.get_executor_type().target.value).lower()
