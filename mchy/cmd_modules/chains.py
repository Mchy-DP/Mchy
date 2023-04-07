
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union
from mchy.cmd_modules.docs_data import DocsData
from mchy.cmd_modules.param import IParam, CtxIParam

from mchy.common.com_types import ComType, ExecType, TypeUnion
from mchy.common.config import Config
from mchy.errors import ContextualisationError, StatementRepError

if TYPE_CHECKING:
    from mchy.cmd_modules.name_spaces import Namespace
    from mchy.contextual.struct.expr import CtxExprNode, CtxExprLits, CtxChainLink, CtxExprPyStruct, CtxPyStruct
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom


class IChainLink(ABC):

    def get_docs(self) -> DocsData:
        return DocsData()

    def __init__(self) -> None:
        super().__init__()
        self.__params_cache: Optional[List[CtxIParam]] = None

    @abstractmethod
    def get_namespace(self) -> 'Namespace':
        ...

    @abstractmethod
    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_params(self) -> Optional[Sequence[IParam]]:
        ...

    def get_extra_param_type(self) -> Optional[Union[ComType, TypeUnion]]:
        """Return the type of any extra positional parameters or None if extra parameters are not allowed"""
        return None

    def get_ctx_params(self) -> Sequence[CtxIParam]:
        if self.__params_cache is None:
            self.__params_cache = []
            _iparams = self.get_params()
            if _iparams is not None:
                for _iparam in _iparams:
                    self.__params_cache.append(CtxIParam(_iparam))
        return self.__params_cache

    def __init_subclass__(cls, abstract: bool = False) -> None:
        if abstract:
            return  # Do not add Abstract chains to the namespace
        new_chain_link = cls()
        new_chain_link.get_namespace().register_new_chain_link(new_chain_link)

    def render(self):  # TODO: improve render to render chains accepting args better
        pred = self.get_predecessor_type()
        return f"({pred.render() if isinstance(pred, ExecType) else ('(...).' + pred.__name__)}).{self.get_name()}: ???"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(ichain=<{self.render()}>)"


class IChain(IChainLink, abstract=True):

    @abstractmethod
    def get_chain_type(self) -> ComType:
        ...

    @abstractmethod
    def get_refined_executor(self) -> ExecType:
        ...

    def yield_const_value(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink']) -> 'CtxExprLits':
        """Will be called to yield a literal, if `.get_chain_type()` returns a constant inert type indicating a literal is expected

        Args:
            executor: The executor of the chain
            chain_links: The chain links the user used to build this chain

        Returns:
            A `CtxExprLits`
        """
        raise ContextualisationError(f"Attempted to get constant value for chain `{type(self).__name__}` however library did not provided a method?")

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        """Will be called to provide the statements to perform this chain, if `.get_chain_type()` returns a non-constant type

        Args:
            executor: The atom containing the executor for this chain
            clink_param_binding: A list of tuples linking all chain-links in this chain to atoms holding the value of any arguments they request
            module: The statement module (Principally for constant atom access)
            function: The statement function of this scope (Principally for any variables this chain may need)
            config: The config this compilation is running with

        Returns:
            A tuple containing, at index 1, the atom holding the output value of this chain-expression and,
            at index 0, the list of statements that must be executed to cause it to take this value.
        """
        raise StatementRepError(f"Attempted to get non-constant value for chain `{type(self).__name__}` however library did not provided a method?")

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        """Will be called to yield a the populated struct, if `.get_chain_type()` returns a struct type

        Args:
            executor: The executor of the chain
            chain_links: The chain links the user used to build this chain
            struct: The struct this node will create an instance of

        Returns:
            A `CtxExprPyStruct`
        """
        raise ContextualisationError(f"Attempted to get struct value for chain `{type(self).__name__}` however library did not provided a method?")

    def render(self):
        return super().render().rstrip("?") + self.get_chain_type().render()
