from typing import List, Tuple, Union
from mchy.common.com_cmd import ComCmd
from mchy.errors import StatementRepError
from mchy.stmnt.struct.atoms import SmtConstInt, SmtVar
from mchy.stmnt.struct.cmds.helpers import resolve_condition_cmd
from mchy.stmnt.struct.linker import SmtLinker
from mchy.stmnt.struct.abs_cmd import SmtCmd


class SmtRawCmd(SmtCmd):

    def __init__(self, raw_cmd: str) -> None:
        self.raw_cmd: str = raw_cmd

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.raw_cmd})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"{self.raw_cmd}")]


class SmtConditionalRawCmd(SmtCmd):

    def __init__(self, conditions: List[Tuple[Union[SmtConstInt, SmtVar], bool]], raw_cmd: str) -> None:
        # conditions: A list of atoms and if they must resolve true or false for the target func/frag to be called
        if len(conditions) == 0:
            raise StatementRepError("ConditionalInvokeFuncCmd has no conditions attached")
        self.conditions: List[Tuple[Union[SmtConstInt, SmtVar], bool]] = conditions
        self.raw_cmd: str = raw_cmd

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.raw_cmd})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        cmd: str = ("execute " + resolve_condition_cmd(self.conditions, linker, stack_level)).strip(" ") + " run " + self.raw_cmd
        return [ComCmd(cmd)]
