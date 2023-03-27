
from typing import List, Tuple

from mchy.common.com_cmd import ComCmd
from mchy.stmnt.struct.linker import SmtLinker
from mchy.stmnt.struct import SmtAtom, SmtCmd
from mchy.stmnt.struct.atoms import SmtConstStr


class SmtSimpleStrConstTellrawCmd(SmtCmd):

    def __init__(self, *msg: SmtConstStr) -> None:
        self.msgs: Tuple[SmtConstStr, ...] = tuple(msg)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.msgs})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        cmd_text = 'tellraw @p ["",'
        for msg in self.msgs:
            cmd_text += '{"text":"'+msg.value.replace('"', '\\"')+'","color":"white"},'
        cmd_text = cmd_text[:-1] + ']'
        return [ComCmd(cmd_text)]
