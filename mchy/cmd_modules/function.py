from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Collection, Dict, List, Optional, Sequence, Tuple, Union
from mchy.cmd_modules.docs_data import DocsData
from mchy.cmd_modules.param import CtxIParam, IParam
from mchy.common.abs_ctx import AbsCtxFunc, AbsCtxParam
from mchy.common.com_types import ComType, ExecType, TypeUnion
from mchy.common.config import Config
from mchy.errors import ContextualisationError

if TYPE_CHECKING:
    from mchy.cmd_modules.name_spaces import Namespace
    from mchy.contextual.struct.expr import CtxExprNode
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom


class CtxIFunc(AbsCtxFunc):

    def __init__(self, ifunc: 'IFunc') -> None:
        self._ifunc = ifunc
        self._params: List[CtxIParam] = [CtxIParam(iparam) for iparam in ifunc.get_params()]

    def get_executor(self) -> ExecType:
        return self._ifunc.get_executor_type()

    def get_name(self) -> str:
        return self._ifunc.get_name()

    def get_params(self) -> Sequence[CtxIParam]:
        return tuple(self._params)

    def get_param(self, name: str) -> Optional[CtxIParam]:
        for param in self._params:
            if param.get_label() == name:
                return param
        return None

    def allow_extra_args(self) -> bool:
        return self._ifunc.get_extra_param_type() is not None

    def get_extra_args_type(self) -> Union[TypeUnion, ComType]:
        ptype = self._ifunc.get_extra_param_type()
        if ptype is not None:
            return ptype
        else:
            raise ContextualisationError(f"Cannot request extra args type of function not accepting extra args {self.render()}")

    def get_return_type(self) -> ComType:
        return self._ifunc.get_return_type()

    def stmnt_conv(
                self,
                executor: 'SmtAtom',
                param_binding: Dict[CtxIParam, 'SmtAtom'],
                extra_binding: List['SmtAtom'],
                module: 'SmtModule',
                function: 'SmtFunc',
                config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        return self._ifunc.stmnt_conv(executor, {param.get_label(): binding for param, binding in param_binding.items()}, extra_binding, module, function, config=config)


class IFunc:

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
    def get_params(self) -> Sequence[IParam]:
        ...

    def get_extra_param_type(self) -> Optional[Union[ComType, TypeUnion]]:
        """Return the type of any extra positional parameters or None if extra parameters are not allowed"""
        return None

    @abstractmethod
    def get_return_type(self) -> ComType:
        ...

    @abstractmethod
    def stmnt_conv(
                self, executor: 'SmtAtom', param_binding: Dict[str, 'SmtAtom'], extra_binding: List['SmtAtom'], module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        ...

    def __init_subclass__(cls) -> None:
        new_function = cls()
        new_function.get_namespace().register_new_func(new_function)

    def get_ctx_func(self) -> CtxIFunc:
        return CtxIFunc(self)
