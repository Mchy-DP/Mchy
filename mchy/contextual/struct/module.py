

from typing import List, Optional, Sequence, Tuple, TypeGuard, Union
from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import CtxIFunc
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.properties import IProp
from mchy.common.abs_ctx import AbsCtxFunc
from mchy.common.com_diff import did_you_mean_opt, how_similar, render_did_you_mean
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertType, StructType, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.ctx_func import CtxMchyFunc
from mchy.contextual.struct.expr import CtxChainLink, CtxChain, CtxPyStruct
from mchy.common.com_inclusion import FileInclusion
from mchy.contextual.struct.stmnt import CtxStmnt
from mchy.contextual.struct.var_scope import VarScope
from mchy.errors import ConversionError


class CtxModule:

    def __init__(self, config: Config) -> None:
        self._config: Config = config
        self.global_var_scope: VarScope = VarScope()
        self.exec_body: List[CtxStmnt] = []
        self._functions: List[AbsCtxFunc] = []
        self._props: List[IProp] = []
        self._chain_links: List[IChainLink] = []
        self._structs: List[CtxPyStruct] = []
        self._ticking_funcs: List[CtxMchyFunc] = []
        self._public_funcs: List[CtxMchyFunc] = []
        self._inclusions: List[FileInclusion] = []

    def add_inclusion(self, new_inc: FileInclusion) -> None:
        self._inclusions.append(new_inc)

    def get_inclusions(self) -> Tuple[FileInclusion, ...]:
        return tuple(self._inclusions)

    def func_defined(self, executor: ExecType, name: str) -> bool:
        return self.get_function(executor, name) is not None

    def get_function(self, executor: ExecType, name: str) -> Optional[AbsCtxFunc]:
        for func in self._functions:
            exec_type = func.get_executor()
            if func.get_name() == name and matches_type(ExecType(exec_type.target, (exec_type.target != ExecCoreTypes.WORLD)), executor):
                return func
        return None

    def get_did_you_mean_for_name(self, bad_name: str) -> Optional[str]:
        """Get 'Did you mean' suggestions for a given function/property name"""

        # get close options
        close_func_names = did_you_mean_opt(bad_name, [func.get_name() for func in self._functions])
        close_prop_names = did_you_mean_opt(bad_name, [prop.get_name() for prop in self._props])
        close_clink_names = did_you_mean_opt(bad_name, [clink.get_name() for clink in self._chain_links if isinstance(clink.get_predecessor_type(), ExecType)])

        # combine results
        combined_close_names: List[Tuple[str, str, float]] = [
            *[("The function", name, how_similar(bad_name, name)) for name in close_func_names],
            *[("The property", name, how_similar(bad_name, name)) for name in close_prop_names],
            *[("The chain", name, how_similar(bad_name, name)) for name in close_clink_names]
        ]

        # cut options down to best 3
        best_options = list(sorted(combined_close_names, key=lambda x: x[2], reverse=True))[:3]

        # Return 'did you mean' string
        return render_did_you_mean([f"{prefix} '{name}'" for prefix, name, closeness in best_options])

    def get_function_oerr(self, executor: ExecType, name: str) -> AbsCtxFunc:
        func = self.get_function(executor, name)
        if func is None:
            raise TypeError("Function unexpectedly doesn't exist")
        return func

    def add_function(self, new_func: AbsCtxFunc) -> None:
        for func in self._functions:
            if ((func.get_name() == new_func.get_name()) and
                    (matches_type(func.get_executor(), new_func.get_executor()) or matches_type(new_func.get_executor(), func.get_executor()))):
                raise ConversionError(
                    f"Function of name `{new_func.get_name()}` is already defined as `{func.render()}` cannot define it as `{new_func.render()}`"
                ).with_loc(new_func.get_signature_loc())
        self._functions.append(new_func)

    def register_as_ticking(self, func: CtxMchyFunc) -> None:
        self._ticking_funcs.append(func)

    def register_as_public(self, new_pfunc: CtxMchyFunc) -> None:
        for pfunc in self._public_funcs:
            if new_pfunc.get_name() == pfunc.get_name():
                raise ConversionError(
                    f"Got Multiple functions marked as public with the same name (`{pfunc.render()}` and `{new_pfunc.render()}`)"
                ).with_loc(new_pfunc.get_signature_loc())
        self._public_funcs.append(new_pfunc)

    def get_ticking_funcs(self) -> List[CtxMchyFunc]:
        return self._ticking_funcs

    def get_public_funcs(self) -> List[CtxMchyFunc]:
        return self._public_funcs

    def get_mchy_functions(self) -> List[CtxMchyFunc]:
        out_funcs: List[CtxMchyFunc] = []
        for func in self._functions:
            if isinstance(func, CtxMchyFunc):
                out_funcs.append(func)
        return out_funcs

    def get_import_functions(self) -> List[CtxIFunc]:
        out_funcs: List[CtxIFunc] = []
        for func in self._functions:
            if isinstance(func, CtxIFunc):
                out_funcs.append(func)
        return out_funcs

    def get_struct(self, name: str) -> Optional[CtxPyStruct]:
        for struct in self._structs:
            if struct.get_name() == name:
                return struct
        return None

    def get_property(self, executor: ExecType, name: str) -> Optional[IProp]:
        for prop in self._props:
            if name == prop.get_name() and matches_type(prop.get_executor_type(), executor):
                return prop
        return None

    def get_chain_link(self, predecessor: Union[CtxChainLink, ExecType], name: str, chain_loc: ComLoc) -> Optional[CtxChainLink]:
        for chain_link in self._chain_links:
            pred_type = chain_link.get_predecessor_type()
            if name == chain_link.get_name():
                if (
                            (isinstance(predecessor, ExecType) and isinstance(pred_type, ExecType)) and (matches_type(pred_type, predecessor)) or
                            (isinstance(predecessor, CtxChainLink) and isinstance(pred_type, type)) and (predecessor.is_iclick_of_type(pred_type))
                        ):
                    if isinstance(chain_link, IChain):
                        return CtxChain(chain_link, chain_loc, self)
                    else:
                        return CtxChainLink(chain_link, chain_loc)
        return None

    def get_property_oerr(self, executor: ExecType, name: str) -> IProp:
        prop = self.get_property(executor, name)
        if prop is None:
            raise TypeError("Property unexpectedly doesn't exist")
        return prop

    def add_prop(self, new_prop: IProp) -> None:
        for prop in self._props:
            if ((prop.get_name() == new_prop.get_name()) and
                    (matches_type(prop.get_executor_type(), new_prop.get_executor_type()) or matches_type(new_prop.get_executor_type(), prop.get_executor_type()))):
                raise ConversionError(f"Property of name `{new_prop.get_name()}` is already defined as `{prop.render()}` cannot define it as `{new_prop.render()}`")
        self._props.append(new_prop)

    def add_chain_link(self, new_chain_link: IChainLink) -> None:
        # Check new chain_link will not clash with any other expression
        for chain_link in self._chain_links:
            cl_pred = chain_link.get_predecessor_type()
            ncl_pred = new_chain_link.get_predecessor_type()
            if (
                    # The names match
                    (chain_link.get_name() == new_chain_link.get_name()) and ((
                        # And both chain links are preceded by a chain link which matches
                        isinstance(cl_pred, IChainLink) and isinstance(ncl_pred, IChainLink) and (cl_pred == ncl_pred)) or (
                        # Or both chain links are executable types which match
                        isinstance(cl_pred, ExecType) and isinstance(ncl_pred, ExecType) and (matches_type(cl_pred, ncl_pred) or matches_type(cl_pred, ncl_pred))
                    ))):
                raise ConversionError(f"Chained Expression `{new_chain_link.render()}` is already defined as `{chain_link.render()}`, Definitions preclude each other.")
        # Check constant-type chains have a yield_const_value method defined
        if isinstance(new_chain_link, IChain):
            new_chain_type = new_chain_link.get_chain_type()
            if isinstance(new_chain_type, InertType) and new_chain_type.const:
                if (IChain.yield_const_value == new_chain_link.__class__.yield_const_value):
                    self._config.logger.warn(
                        f"Library warning: Chain `{type(new_chain_link).__name__}` from namespace `{new_chain_link.get_namespace().render()}` " +
                        f"reports a constant type but does not implement `yield_const_value` which is required for it to be usable"
                    )
            elif isinstance(new_chain_type, StructType):
                if (IChain.yield_struct_instance == new_chain_link.__class__.yield_struct_instance):
                    self._config.logger.warn(
                        f"Library warning: Chain `{type(new_chain_link).__name__}` from namespace `{new_chain_link.get_namespace().render()}` " +
                        f"reports a struct type but does not implement `yield_struct_instance` which is required for it to be usable"
                    )
            else:
                if (IChain.stmnt_conv == new_chain_link.__class__.stmnt_conv):
                    self._config.logger.warn(
                        f"Library warning: Chain `{type(new_chain_link).__name__}` from namespace `{new_chain_link.get_namespace().render()}` " +
                        f"reports a non-constant type but does not implement `stmnt_conv` which is required for it to be usable"
                    )
        self._chain_links.append(new_chain_link)

    def add_struct(self, new_struct: CtxPyStruct) -> None:
        for existing_struct in self._structs:
            if (new_struct.get_name() == existing_struct.get_name()):
                raise ConversionError(f"Struct of name `{new_struct.get_name()}` is already defined as `{new_struct.render()}` cannot define it as `{existing_struct.render()}`")
        self._structs.append(new_struct)

    def import_ns(self, ns: Namespace) -> None:
        for function in ns.ifuncs:
            self.add_function(function.get_ctx_func())
        for prop in ns.iprops:
            self.add_prop(prop)
        for chain in ns.ichain_links:
            self.add_chain_link(chain)
        for struct in ns.istructs:
            self.add_struct(CtxPyStruct(struct))

    def get_cont_of_clink(self, chain_link: IChainLink) -> List[IChainLink]:
        return [
            clink for clink in self._chain_links if (  # Return every chain link where
                (not isinstance((pred_type := clink.get_predecessor_type()), ExecType)) and  # predecessor type is IChainLink
                isinstance(chain_link, pred_type)  # & The IChainLink Matches
            )
        ]

    def get_terminal_cont_of_clink(self, chain_link: IChainLink) -> List[IChain]:
        return [click for click in self.get_cont_of_clink(chain_link) if isinstance(click, IChain)]
