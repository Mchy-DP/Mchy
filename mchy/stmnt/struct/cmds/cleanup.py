
from typing import List

from mchy.common.com_cmd import ComCmd
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.linker import SmtLinker


class SmtCleanupTag(SmtCmd):

    def __init__(self, tag: str) -> None:
        self.tag: str = tag

    def __repr__(self) -> str:
        return f"{type(self).__name__}(tag = {self.tag})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"tag @e remove {self.tag}")]
