

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List
from mchy.common.com_cmd import ComCmd

if TYPE_CHECKING:
    from mchy.stmnt.struct.linker import SmtLinker


class SmtCmd(ABC):

    @abstractmethod
    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        """Generate the literal minecraft commands that accomplish this statement

        Args:
            linker: The class holding linking information between smt objects and virtual locations
            stack_level: The current recursion depth/number of `stack frames` below this one

        Returns:
            List[ComCmd]: The list of commands to perform this statements action
        """
        ...
