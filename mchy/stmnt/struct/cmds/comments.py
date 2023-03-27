
from enum import Enum
from typing import List, Optional
from mchy.common.com_cmd import ComCmd
from mchy.stmnt.struct.linker import SmtLinker
from mchy.stmnt.struct.abs_cmd import SmtCmd


class CommentImportance(Enum):
    NORMAL = 0
    SUBSUBHEADING = 1
    SUBHEADING = 2
    HEADING = 3
    TITLE = 4


class SmtCommentCmd(SmtCmd):
    """Statement to add a comment in the output datapack"""

    def __init__(self, comment_text: str, *, generator: Optional[str] = "MCHY", importance: CommentImportance = CommentImportance.NORMAL) -> None:
        self.comment: str = comment_text
        self.generator: Optional[str] = generator
        self.importance: CommentImportance = importance

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.generator}: {self.comment if len(self.comment) < 25 else self.comment[:24]+'…'})"

    def _get_generator_prefix(self) -> str:
        if self.generator is None:
            return "# "
        else:
            return f"## {self.generator} ##: "

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        lines: List[str] = []

        if self.importance == CommentImportance.TITLE:
            lines.append("#" * 75)
            lines.append(f" {self.comment} ".center(75, "#"))
            lines.append("#" * 75)
        elif self.importance == CommentImportance.HEADING:
            lines.append(f"===== {self.comment} =====")
        elif self.importance == CommentImportance.SUBHEADING:
            lines.append(f"----- {self.comment} -----")
        elif self.importance == CommentImportance.SUBSUBHEADING:
            lines.append(f"--- {self.comment}")
        elif self.importance == CommentImportance.NORMAL:
            lines.append(f"{self.comment}")

        return [ComCmd(self._get_generator_prefix() + line) for line in lines]
