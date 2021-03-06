from io import StringIO
import parser.parser as p
from enum import Enum
from lexer.utils import clean


# from .grammar import Grammar

class ParseTypes(Enum):
    LINK = p.LinkP
    TEMPLATE = p.TemplateP


class Compiler:
    def __init__(self):
        self.writer = StringIO()
        # self.grammar = Grammar()
        self.parser = p.Parser()

    def render(self, node):
        """ Render function """
        self.writer = StringIO()
        node.compile(self.writer, self.parser)
        result = self.writer.getvalue()
        self.writer.close()
        return result

    def compile(self, text):
        ast = self.parser.parse(text)
        # print(ast)
        return clean(self.render(ast))

    def on(self, fn, parse_type):
        return self.parser.on(fn, parse_type)
