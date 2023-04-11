
from mchy.built.MchyParser import MchyParser
from antlr4.CommonTokenFactory import CommonTokenFactory
from antlr4 import CommonTokenStream


class MchyCustomParser(MchyParser):

    def getTokenFactory(self) -> CommonTokenFactory:  # Type hinting redefine
        return super().getTokenFactory()

    def getTokenStream(self) -> CommonTokenStream:  # Type hinting redefine
        return super().getTokenStream()
