
from typing import Any, Dict, List, Optional, Set, Tuple
from mchy.cmd_modules.function import CtxIFunc, CtxIParam
from mchy.common.config import Config
from mchy.contextual.struct import CtxMchyFunc
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstStr, SmtConstFloat, SmtConstNull, SmtConstInt, SmtWorld
from mchy.stmnt.struct.cmds import SmtInvokeFuncCmd
from mchy.stmnt.struct.function import SmtFunc, SmtMchyFunc, SmtGhostFunc
from mchy.stmnt.gen_expr import convert_expr


class SmtModule:

    def __init__(self) -> None:
        self._mchy_funcs_link: Dict[CtxMchyFunc, SmtMchyFunc] = {}
        self.setup_function: SmtFunc = SmtGhostFunc()  # The function that is ran to setup required structures (Such as late scoreboard creation etc)
        self.initial_function: SmtFunc = SmtFunc()  # The function that is ran on reload to produce the effects of global scope code
        self.ticking_function: SmtFunc = SmtFunc()  # The function that is ran every tick
        self.import_ns_function: SmtFunc = SmtGhostFunc()  # generates code to ensure that default-iparam's pseudo-vars have the correct value
        self._int_consts: Dict[int, SmtConstInt] = {}
        self.ctx_decl_func: Set[CtxMchyFunc] = set()
        self._ctx_iparam_defaults: Dict[CtxIParam, Optional[SmtAtom]] = {}
        self._world_lit_val = SmtWorld()

        # Ensures before any global scope code runs the imported functions are fully loaded
        self.setup_function.func_frag.body.append(SmtInvokeFuncCmd(self.import_ns_function, self.get_world()))

    def get_smt_func(self, ctx_func: CtxMchyFunc) -> SmtMchyFunc:
        return self._mchy_funcs_link[ctx_func]

    def get_const_with_val(self, value: int) -> SmtConstInt:
        if value not in self._int_consts.keys():
            self._int_consts[value] = SmtConstInt(value)
        return self._int_consts[value]

    def get_all_int_consts(self) -> List[SmtConstInt]:
        return list(self._int_consts.values())

    def get_str_const(self, value: str) -> SmtConstStr:
        return SmtConstStr(value)

    def get_float_const(self, value: float) -> SmtConstFloat:
        return SmtConstFloat(value)

    def get_null_const(self) -> SmtConstNull:
        return SmtConstNull()

    def get_world(self) -> SmtWorld:
        return self._world_lit_val

    def get_ifunc_param_default_atom(self, param: CtxIParam, config: Config) -> Optional[SmtAtom]:
        """
        Return the atom containing the default value of the supplied `param` or None if no default exists
        """
        if param not in self._ctx_iparam_defaults:
            default_ctx_expr = param.get_default_ctx_expr()
            default_cmds, default_atom = (convert_expr(default_ctx_expr, self, self.import_ns_function, config=config) if default_ctx_expr is not None else ([], None))
            self.import_ns_function.func_frag.body.extend(default_cmds)
            self._ctx_iparam_defaults[param] = default_atom
        return self._ctx_iparam_defaults[param]

    def register_new_mchy_function(self, func: CtxMchyFunc) -> None:
        self._mchy_funcs_link[func] = SmtMchyFunc(self.initial_function, func)

    def get_smt_mchy_funcs(self) -> Tuple[SmtMchyFunc, ...]:
        return tuple(self._mchy_funcs_link.values())
