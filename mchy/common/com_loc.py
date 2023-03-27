
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ComLoc:
    line: Optional[int] = None
    col_start: Optional[int] = None
    line_end: Optional[int] = None
    col_end: Optional[int] = None

    @property
    def line_start_int(self) -> int:
        """Get the start line raising a ValueError if it is not defined"""
        if self.line is None:
            raise ValueError("Line start not defined")
        return self.line

    @property
    def line_end_int(self) -> int:
        """Get the end line raising a ValueError if it is not defined"""
        if self.line_end is None:
            raise ValueError("Line end not defined")
        return self.line_end

    @property
    def col_start_int(self) -> int:
        """Get the line raising a ValueError if it is not defined"""
        if self.col_start is None:
            raise ValueError("Col start not defined")
        return self.col_start

    @property
    def col_end_int(self) -> int:
        """Get the line raising a ValueError if it is not defined"""
        if self.col_end is None:
            raise ValueError("Col end not defined")
        return self.col_end

    def with_line(self, line: Optional[int]) -> 'ComLoc':
        return ComLoc(line, self.col_start, self.line_end, self.col_end)

    def with_col(self, start: Optional[int]) -> 'ComLoc':
        return ComLoc(self.line, start, self.line_end, self.col_end)

    def with_line_end(self, line_end: Optional[int]) -> 'ComLoc':
        return ComLoc(self.line, self.col_start, line_end, self.col_end)

    def with_col_end(self, col_end: Optional[int]) -> 'ComLoc':
        return ComLoc(self.line, self.col_start, self.line_end, col_end)

    def render(self) -> str:
        if (self.line_end is None) or self.line == self.line_end:
            if (self.col_end is None) or self.col_start == self.col_end:
                return f"{self.line}:{self.col_start}"
            return f"{self.line}:{self.col_start}..{self.col_end}"
        return f"{self.line}:{self.col_start}..{self.line_end}:{self.col_end}"

    def union(self, other: 'ComLoc') -> 'ComLoc':
        # Line start
        line_start: Optional[int] = None
        col_start: Optional[int] = None
        if self.line is None:
            line_start = other.line
            col_start = other.col_start
        elif other.line is None:
            line_start = self.line
            col_start = self.col_start
        else:
            if self.line < other.line:
                line_start = self.line
                col_start = self.col_start
            elif self.line == other.line:
                line_start = self.line
                if self.col_start is None:
                    col_start = other.col_start
                elif other.col_start is None:
                    col_start = self.col_start
                else:
                    col_start = min(self.col_start, other.col_start)
            else:
                line_start = other.line
                col_start = other.col_start

        # Line End
        line_end: Optional[int] = None
        col_end: Optional[int] = None
        if self.line_end is None:
            line_end = other.line_end
            col_end = other.col_end
        elif other.line_end is None:
            line_end = self.line_end
            col_end = self.col_end
        else:
            if self.line_end < other.line_end:
                line_end = other.line_end
                col_end = other.col_end
            elif self.line_end == other.line_end:
                line_end = self.line_end
                if self.col_end is None:
                    col_end = other.col_end
                elif other.col_end is None:
                    col_end = self.col_end
                else:
                    col_end = max(self.col_end, other.col_end)
            else:
                line_end = self.line_end
                col_end = self.col_end

        # Return ComLoc
        return ComLoc(line_start, col_start, line_end, col_end)
