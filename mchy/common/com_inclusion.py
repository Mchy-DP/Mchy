

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, eq=True)
class FileInclusion:
    resource_path: str
    output_path: List[str]
