
from typing import List, Tuple, Union
from mchy.common.com_cmd import ComCmd
from mchy.errors import StatementRepError
from mchy.stmnt.helpers import smt_get_exec_vdat
from mchy.stmnt.struct.cmds.helpers import resolve_condition_cmd
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstInt, SmtVar, SmtWorld
from mchy.stmnt.struct.function import SmtFunc, SmtMchyFunc
from mchy.stmnt.struct.smt_frag import SmtFragment


def invoke_prefix_create(executor: SmtAtom, linker: SmtLinker):
    if isinstance(executor, SmtWorld):
        return ""
    exec_vdat = smt_get_exec_vdat(executor, linker)
    return f"execute as {exec_vdat.get_selector()} run "


class SmtInvokeFuncCmd(SmtCmd):

    def __init__(self, target_func: SmtFunc, executor: SmtAtom) -> None:
        self.target_func: SmtFunc = target_func
        self.executor: SmtAtom = executor

    @property
    def func_id(self):
        return self.target_func.id

    def __repr__(self) -> str:
        return f"{type(self).__name__}(call_id={self.func_id})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        prefix: str = ""
        if isinstance(self.target_func, SmtMchyFunc):
            prefix = invoke_prefix_create(self.executor, linker)
        return [ComCmd(f"{prefix}function {linker.lookup_func(self.target_func, stack_level + 1)}")]


class SmtConditionalInvokeFuncCmd(SmtCmd):

    def __init__(self, conditions: List[Tuple[Union[SmtConstInt, SmtVar], bool]], target_func: SmtFunc, ext_frag: SmtFragment, executor: SmtAtom) -> None:
        # conditions: A list of atoms and if they must resolve true or false for the target func/frag to be called
        if len(conditions) == 0:
            raise StatementRepError("ConditionalInvokeFuncCmd has no conditions attached")
        self.conditions: List[Tuple[Union[SmtConstInt, SmtVar], bool]] = conditions
        self.target_func: SmtFunc = target_func
        self.ext_frag: SmtFragment = ext_frag
        self.executor: SmtAtom = executor

    @property
    def func_id(self):
        return self.target_func.id

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(call_id={self.func_id}, frag={self.ext_frag.get_frag_name()}, conditions=[" +
            (', '.join(f'({atom}: {expect})' for atom, expect in self.conditions)) + "])"
        )

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        # resolve conditions
        cmd: str = ("execute " + resolve_condition_cmd(self.conditions, linker, stack_level)).strip(" ")
        cmd += f" run "
        # resolve prefix:
        if isinstance(self.target_func, SmtMchyFunc):
            cmd += invoke_prefix_create(self.executor, linker)
        # build final command
        cmd += f"function {linker.lookup_frag(self.target_func, stack_level, self.ext_frag)}"
        return [ComCmd(cmd)]
