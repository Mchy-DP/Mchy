
from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Type, TypeVar
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.param import CtxIParam
from mchy.common.abs_ctx import AbsCtxParam
from mchy.common.com_loc import ComLoc
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitFloat, CtxExprLitInt

from mchy.errors import ContextualisationError, ConversionError, UnreachableError
from mchy.common.com_types import ComType, ExecType, InertType, StructType, matches_type
from mchy.contextual.struct.expr.abs_node import CtxExprNode, CtxExprLits
from mchy.contextual.struct.expr.structs import CtxExprPyStruct, CtxPyStruct

if TYPE_CHECKING:
    from mchy.stmnt.struct import SmtModule, SmtFunc, SmtCmd, SmtAtom
    from mchy.contextual.struct.module import CtxModule


T = TypeVar("T", bound=CtxExprNode)


class CtxChainLink:

    def __init__(self, chain_link: IChainLink) -> None:
        self._chain_link: IChainLink = chain_link
        self._chain_data: Optional[Dict[CtxIParam, Optional[CtxExprNode]]] = None  # None means unset
        self._extra_args: Optional[List[CtxExprNode]] = None  # None means unset

    @property
    def expects_args(self) -> bool:
        return self._chain_link.get_params() is not None

    @property
    def ichainlink(self) -> IChainLink:
        return self._chain_link

    def get_link_name(self) -> str:
        return self._chain_link.get_name()

    def opt_get_executor_render(self) -> str:
        pred_type = self._chain_link.get_predecessor_type()
        if isinstance(pred_type, ExecType):
            return pred_type.render()
        return "(...)"

    def render(self) -> str:
        return self._chain_link.render()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(IChainLink={repr(self._chain_link)}, data={repr(self._chain_data)})"

    def set_chain_data(self, chain_data: Optional[Dict[AbsCtxParam, Optional['CtxExprNode']]], extra_args: List[CtxExprNode] = []) -> None:
        # None on the interface means no-data None internally means not set so None must be converted to an empty dict
        if chain_data is None:
            chain_data = {}
        # Validation
        if set(chain_data.keys()) != set(self.get_ctx_params()):
            raise ContextualisationError(f"Not all parameters have a value supplied: {set(self.get_ctx_params()).difference(set(chain_data.keys()))}")
        validated_chain_data: Dict[CtxIParam, Optional[CtxExprNode]] = {}
        for param, binding in chain_data.items():
            if binding is None:
                if not param.is_defaulted():
                    raise ConversionError(f"Non-optional argument `{self.render()}` has no value")
            else:
                ptype = param.get_param_type()
                if isinstance(ptype, InertType) and ptype.const and (not isinstance(binding, CtxExprLits)):
                    raise ContextualisationError(f"Type Error: parameter ({self.render()}) with constant type is not assigned to literal node")
                if not matches_type(ptype, binding.get_type()):
                    raise ConversionError(
                        f"Parameter `{param.get_label()}` from chain `{self.render()}` is of type `{binding.get_type().render()}`, `{ptype.render()}` expected"
                    ).with_loc(binding.loc)
            if not isinstance(param, CtxIParam):
                raise ContextualisationError(f"Non-CtxIParam `{type(param).__name__}({param.render()})` encountered setting chain-link data of `{self.render()}`")
            validated_chain_data[param] = binding
        # Set data
        self._chain_data = validated_chain_data
        # extra args validate & set
        expected_extra_param_type = self._chain_link.get_extra_param_type()
        if expected_extra_param_type is None:
            if len(extra_args) >= 1:
                raise ContextualisationError(f"ChainLink start unexpectedly parsed with extra args despite disallowing them (link: `{self._chain_link.render()}`)")
        else:
            for aix, arg in enumerate(extra_args):
                if not matches_type(expected_extra_param_type, arg.get_type()):
                    raise ConversionError(
                        f"Extra agument at index {aix} of chain {self._chain_link.render()} is of invalid type, found: " +
                        f"`{arg.get_type().render()}` expected `{expected_extra_param_type.render()}`"
                    )
        self._extra_args = extra_args

    def get_ctx_params(self) -> Sequence[CtxIParam]:
        return self._chain_link.get_ctx_params()

    def get_ctx_param(self, name: str) -> Optional[CtxIParam]:
        for param in self.get_ctx_params():
            if param.get_label() == name:
                return param
        return None

    def get_arg_for_param(self, param: CtxIParam) -> 'CtxExprNode':
        if self._chain_data is None:
            raise ContextualisationError(f"Arg `{param.render()}` requested from chain ({self.render()}) with unset data")
        arg_value: Optional[CtxExprNode] = self._chain_data[param]
        if arg_value is None:
            arg_value = param.get_default_ctx_expr()
            if arg_value is None:
                raise ContextualisationError(f"Arg `{param.render()}` relies on a default value that doesn't exist")
        return arg_value

    def is_iclick_of_type(self, ichain_link_type: Type[IChainLink]):
        return isinstance(self._chain_link, ichain_link_type)

    def get_arg_for_param_described(self, param_name: str, arg_node_type: Type[T], fuzzy: bool = True) -> T:
        param, arg = self._get_param_arg_of_name(param_name)
        if not isinstance(arg, arg_node_type):
            if fuzzy and (arg_node_type == CtxExprLitFloat) and isinstance(arg, CtxExprLitInt):
                return CtxExprLitFloat(float(arg.value), src_loc=arg.loc)  # type:ignore  # false positive as mypy doesn't understand `T === CtxExprLitFloat` here
            raise ContextualisationError(
                f"Argument for parameter `{param.render()}` of `{self.render()}` is of type `{type(arg).__name__}`, `{arg_node_type.__name__}` requested?"
            )
        return arg

    def _get_param_arg_of_name(self, param_name: str) -> Tuple[CtxIParam, CtxExprNode]:
        param = self.get_ctx_param(param_name)
        if param is None:
            raise ContextualisationError(
                f"Param of name `{param_name}` doesn't exist for `{self.render()}`.  Valid params are: " +
                f"[{', '.join(param.render() for param in self.get_ctx_params())}]"
            )
        return param, self.get_arg_for_param(param)

    def get_arg_for_param_of_name(self, param_name: str) -> CtxExprNode:
        return self._get_param_arg_of_name(param_name)[1]

    def get_extra_args(self) -> List[CtxExprNode]:
        if self._extra_args is None:
            raise ContextualisationError(f"Extra args requested from chain ({self.render()}) with unset data")
        return self._extra_args

    def allow_extra_args(self) -> bool:
        return self._chain_link.get_extra_param_type() is not None


Self = TypeVar("Self", bound='CtxChain')


class CtxChain(CtxChainLink):

    def __init__(self, chain: IChain, module: 'CtxModule') -> None:
        super().__init__(chain)
        self.chain: IChain = chain
        self._struct: Optional[CtxPyStruct] = None  # Stores the struct if this chain is associated with one
        chain_type = self.get_chain_type()
        if isinstance(chain_type, StructType):
            self._struct = module.get_struct(chain_type.target.name)
            if self._struct is None:
                raise ContextualisationError(f"Cannot find struct associated with type `{chain_type.render()}`")

    def get_chain_type(self) -> ComType:
        return self.chain.get_chain_type()

    def __repr__(self) -> str:
        return super().__repr__()  # Super is actually sufficient

    def yield_const_value(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink']) -> 'CtxExprLits':
        return self.chain.yield_const_value(executor, chain_links)

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink']) -> 'CtxExprPyStruct':
        if self._struct is None:
            raise ContextualisationError(f"Struct unexpectedly missing for chain of struct type")
        return self.chain.yield_struct_instance(executor, chain_links, struct=self._struct)


class CtxExprGenericChain(CtxExprNode):

    @staticmethod
    def start(executor: CtxExprNode) -> 'CtxExprPartialChain':
        return CtxExprPartialChain(executor, [], src_loc=ComLoc())

    @abstractmethod
    def new_with_link(self, new_link: CtxChainLink, link_loc: ComLoc) -> 'CtxExprGenericChain':
        ...


class CtxExprPartialChain(CtxExprGenericChain):

    def __init__(self, executor: CtxExprNode, chaining: List[CtxChainLink], **kwargs):
        """DO NOT CALL DIRECTLY: use `cls.start()` - Inconsistent Final chains marked as partial may result"""
        super().__init__([executor], **kwargs)
        self._executor: CtxExprNode = executor
        self._chaining: List[CtxChainLink] = chaining

    def _get_type(self) -> ComType:
        raise ConversionError(f"Type cannot be found for a partial chain `{self.render()}`")

    def flatten(self) -> 'CtxExprNode':
        return self._flatten_children()  # The type of CtxExprPartialChain cannot be queried

    def _flatten_children(self) -> 'CtxExprNode':
        return CtxExprPartialChain(self._executor.flatten(), self._chaining, src_loc=self.loc)

    def _flatten_body(self) -> 'CtxExprLits':
        raise UnreachableError(f"Partial Chains cannot be flattened to literal values")  # Should never get raised as `.get_type()` should crash before this

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprPartialChain) and self._chaining == other._chaining

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f", chaining=[{', '.join(str(link) for link in self._chaining)}])"

    def render(self) -> str:
        if len(self._chaining) >= 1:
            return self._chaining[0].opt_get_executor_render() + "." + ".".join(str(link.get_link_name()) for link in self._chaining)
        return repr(self) + ".render()"

    @property
    def peek(self) -> CtxChainLink:
        """Get readonly access to the active chain-link"""
        return self._chaining[-1]

    def new_with_link(self, new_link: CtxChainLink, link_loc: ComLoc) -> 'CtxExprGenericChain':
        if isinstance(new_link, CtxChain):
            if not matches_type(new_link.chain.get_refined_executor(), self._executor.get_type()):
                raise ConversionError(
                    f"Chain `{new_link.chain.render()}` cannot execute on type {self._executor.get_type().render()}, expected: {new_link.chain.get_refined_executor().render()}"
                )
            return CtxExprFinalChain(self._executor, self._chaining, new_link, src_loc=(link_loc.union(self.loc)))
        else:
            return CtxExprPartialChain(self._executor, self._chaining + [new_link], src_loc=(link_loc.union(self.loc)))


class CtxExprFinalChain(CtxExprGenericChain):

    def __init__(self, executor: CtxExprNode, links: List[CtxChainLink], terminal_link: CtxChain, **kwargs):
        super().__init__([executor], **kwargs)
        self.executor: CtxExprNode = executor
        self._links: List[CtxChainLink] = links
        self._chain: CtxChain = terminal_link

    def get_chain_links(self) -> List[CtxChainLink]:
        return list(self._links) + [self._chain]

    def _get_type(self) -> ComType:
        return self._chain.get_chain_type()

    def _flatten_children(self) -> 'CtxExprNode':
        if isinstance(self.get_type(), StructType):
            return self._chain.yield_struct_instance(self.executor, self.get_chain_links()).with_loc(self.loc)
        else:
            return CtxExprFinalChain(self.executor, self._links, self._chain, src_loc=self.loc)

    def _flatten_body(self) -> 'CtxExprLits':
        return self._chain.yield_const_value(self.executor, self.get_chain_links())

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, CtxExprFinalChain) and self._links == other._links and self._chain == other._chain

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f", links=[{', '.join(str(link) for link in self._links)}], chain={str(self._chain)})"

    def new_with_link(self, new_link: CtxChainLink, link_loc: ComLoc) -> 'CtxExprGenericChain':
        raise NotImplementedError("Complete Chains cannot be further extended currently")

    def render(self) -> str:
        return f"({self.executor.get_type().render()}." + ".".join(
            (link.get_link_name() if not link.expects_args else (
                f"{link.get_link_name()}(" + ", ".join(param.render() for param in link.get_ctx_params()) + ")"
            )) for link in self.get_chain_links()
        ) + ": " + self._chain.get_chain_type().render()

    def stmnt_conv(
            self,
            executor: 'SmtAtom',
            param_binding: Dict[CtxChainLink, Tuple[Dict[AbsCtxParam, 'SmtAtom'], List['SmtAtom']]],
            module: 'SmtModule',
            function: 'SmtFunc',
            config: Config) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        user_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]] = []
        for chain_link, binding in param_binding.items():
            param_binding_dict: Dict[str, 'SmtAtom'] = {}
            extra_arg_list: List['SmtAtom'] = []
            user_param_binding.append((chain_link.ichainlink, param_binding_dict, extra_arg_list))
            for param, atom in binding[0].items():
                param_binding_dict[param.get_label()] = atom
            for arg in binding[1]:
                extra_arg_list.append(arg)
        return self._chain.chain.stmnt_conv(executor, user_param_binding, module, function, config)
