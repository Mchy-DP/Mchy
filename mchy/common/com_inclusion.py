

from dataclasses import dataclass
from typing import List

from mchy.common.com_loc import ComLoc


@dataclass(frozen=True, eq=True)
class FileInclusion:
    resource_path: str
    output_path: List[str]
    loc: ComLoc
