
from dataclasses import dataclass, field as dataclass_field
from typing import Dict, Optional


@dataclass(frozen=True)
class DocsData:
    short_summary: Optional[str] = None
    param_info: Dict[str, str] = dataclass_field(default_factory=dict)
    return_info: Optional[str] = None
    full_description: Optional[str] = None

    def render(self) -> str:
        out = "\n"
        if self.short_summary is not None:
            out += f"{self.short_summary}\n"
        if len(self.param_info) >= 1:
            out += "\n"
            out += f"Params:\n"
            for param_name, pdesc in self.param_info.items():
                out += f"  - **{param_name}**: " + pdesc.replace('\n', '\\\n    ') + "\n"
        if self.return_info is not None:
            out += "\n"
            out += f"Returns:\n  - " + self.return_info.replace('\n', '\\\n    ') + "\n"
        if self.full_description is not None:
            out += "\n"
            out += self.full_description + "\n"
        return out.rstrip("\n").replace("\n", "\n> ").lstrip("\n") + "\n"
