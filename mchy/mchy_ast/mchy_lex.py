
from mchy.built.MchyLexer import MchyLexer


class MchyCustomLexer(MchyLexer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__index_of_last_newline: int = 0

    def cust_hit_newline(self) -> bool:
        self.__index_of_last_newline = self.getCharIndex()
        return True

    def cust_get_index_into_line(self) -> int:
        return (self.getCharIndex() - self.__index_of_last_newline)
