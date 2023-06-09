
from typing import List, Literal, Optional, Sequence, Union
from mchy.common.abs_ctx import AbsCtxFunc, AbsCtxParam
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecType, TypeUnion
from mchy.contextual.struct.stmnt import CtxStmnt, MarkerDeclVar, MarkerParamDefault, MarkerDeclFunc
from mchy.contextual.struct.var_scope import CtxVar, VarScope
from mchy.errors import ContextualisationError, UnreachableError


class CtxMchyParam(AbsCtxParam):

    def __init__(self, label: str, label_loc: ComLoc, param_type: ComType, default_marker: MarkerParamDefault) -> None:
        self._label: str = label
        self._param_type: ComType = param_type
        self.default_marker: MarkerParamDefault = default_marker
        self.linking_decl_mark: MarkerDeclVar = MarkerDeclVar()
        self.linked_scope_var: Optional[CtxVar] = None
        self.label_loc: ComLoc = label_loc

    def get_label(self) -> str:
        return self._label

    def get_param_type(self) -> ComType:  # Mchy params cannot be TypeUnion's
        return self._param_type

    def is_defaulted(self) -> bool:
        return self.default_marker.param_default is not None


class CtxMchyFunc(AbsCtxFunc):

    def __init__(
                self,
                executor: ExecType,
                executor_loc: ComLoc,
                name: str,
                params: List[CtxMchyParam],
                return_type: ComType,
                return_loc: ComLoc,
                def_loc: ComLoc,
                func_loc: ComLoc,
                decl_marker: MarkerDeclFunc
            ) -> None:
        self._executor: ExecType = executor
        self._name: str = name
        self._params: List[CtxMchyParam] = params
        self._return_type: ComType = return_type
        self.decl_marker: MarkerDeclFunc = decl_marker
        self.func_scope: VarScope = VarScope()
        self.exec_body: List[CtxStmnt] = []
        self.executor_loc: ComLoc = executor_loc
        self.return_loc: ComLoc = return_loc
        self.def_loc: ComLoc = def_loc
        self.func_lock: ComLoc = func_loc

        for param in self._params:
            param.linking_decl_mark.with_enclosing_function(self)
            param.linked_scope_var = self.func_scope.register_new_var(param.get_label(), param.get_param_type(), True, param.linking_decl_mark, param.label_loc)

    def get_executor(self) -> ExecType:
        return self._executor

    def get_name(self) -> str:
        return self._name

    def get_params(self) -> Sequence[CtxMchyParam]:
        return tuple(self._params)

    def get_param(self, name: str) -> Optional[CtxMchyParam]:
        for param in self._params:
            if param.get_label() == name:
                return param
        return None

    def allow_extra_args(self) -> Literal[False]:
        return False  # User defined functions cannot have an unknown number of arguments

    def get_extra_args_type(self) -> Union[TypeUnion, ComType]:
        raise ContextualisationError(f"Cannot request extra args type of user-defined function {self.render()}")

    def get_return_type(self) -> ComType:
        return self._return_type

    def get_signature_loc(self) -> ComLoc:
        print("^^^^^ def @ ", self.def_loc.render())
        return ComLoc(line=self.def_loc.line, col_start=self.def_loc.col_start, line_end=self.return_loc.line_end, col_end=self.return_loc.col_end)
