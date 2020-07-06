import logging
import re
import lexer.lexer as lexer
from utils.combinators import ParseError
from parser import grammar as g
from lexer.utils import MalformedTag

logger = logging.getLogger('parser')

"""A recursive descent parser https://en.wikipedia.org/wiki/Recursive_descent_parser
You can find the grammar for Wikimedia in the ABNF form here(https://www.mediawiki.org/wiki/Preprocessor_ABNF),
this parser implements a context-free grammar and each rule is described in the proper method inside Grammar class.
Obviously this parser will not handle every production rule (non-terminal ones), in fact there are rules
that might be simplified and a internal grammar is used and explained in the EBNF form.
"""


class Node:
    """AST
                         Node(None)
            ________________|_______ ....
            |       |              |
    Node(TextP) Node(TemplateP)  LinkNode(LinkP)
                             ______|____
                            |         |
                    Node(Text)       LinkNode(LinkP)
                                      |
                                    ....
    """

    def __init__(self, value=None):
        self.value = value
        self.children = []

    def add(self, node):
        # assert isinstance(node, Node)
        self.children.append(node)

    def __repr__(self):
        NodeVisitor.pretty_print(self)
        return ''

    def compile(self, writer, parser):
        parser.notify(self)
        if self.value:
            # breakpoint()
            self.value.render(writer)

        for children in self.children:
            children.compile(writer, parser)

    # def __eq__(self, node):


class NodeVisitor:
    @staticmethod
    def pretty_print(node, _prefix="", _last=True):
        print(_prefix, "`- " if _last else "|- ", node.value, sep="")
        _prefix += "   " if _last else "|  "
        child_count = len(node.children)
        for i, child in enumerate(node.children):
            _last = i == (child_count - 1)
            NodeVisitor.pretty_print(child, _prefix, _last)

    @staticmethod
    def compare(ast1, ast2):
        pass


class Parser:
    def __init__(self):
        self._tokens = iter([])
        self._ast = Node()
        self._index = -1
        self._current = None
        # self.last = None
        self._listeners = []
        self.lexer = lexer.Lexer()
        # self.expression =
        self._grammar = g.Grammar()

    def parse(self, text, expression=None):
        self._ast = Node()
        try:
            self._tokens = iter(self.lexer.tokenize(text))
            expression = expression if expression else self._grammar.expression()
            self.next()
            while self.current.token != lexer.Lexer.EOF:
                result = expression(self)
                # print(self.current, result)
                if result:
                    self._ast.add(result)
                else:
                    self.next()

        except (MalformedTag, ParseError) as e:
            raise e

        return self._ast

    def next(self):
        try:
            # self.last_token = self._current
            token = next(self._tokens)
            # logging.info('Next token: ' + repr(token))
            self._index = self._index + 1
            self._current = token
            return token
        except StopIteration:
            return None

    @property
    def index(self):
        return self._index

    @property
    def current(self):
        return self._current

    def on(self, fn, type):
        self._listeners.append((fn, type))
        index = len(self._listeners) - 1

        def off():
            if index >= 0:
                self._listeners.pop(index)

        return off

    def notify(self, node):
        if node.value and len(self._listeners) > 0:
            for fn, type in self._listeners:
                if isinstance(node.value, type.value):
                    fn(node)


class Expression:
    def __init__(self, exp):
        self.expression = exp

    def render(self, writer):
        raise NotImplementedError()

    def compile(self, writer, parser):
        return self.render(writer)

    # def value(self):
    #     return self.expression


class LineBreakP(Expression):
    def __init__(self, text):
        super().__init__(text)
        self.text = text

    def render(self, writer):
        pass


class TextP(Expression):
    def __init__(self, text):
        self.text = text

    def render(self, writer):
        writer.write(self.text)
        return self.text


class LinkP(Expression):
    category_match = re.compile(r'(?<=Category:).+')

    def __init__(self, node):
        self.text = node.text
        super().__init__(node)

    def evaluate(self):
        first = self.text.find('|')
        if first < 0:
            return self.text, []
        title = self.text[:first]
        last = 0
        args = []
        t = self.text[first + 1:]
        for i in re.finditer(r'\|', t):
            arg = t[last:i.end() - 1]
            last = i.end()
            args.append(arg)

        if last <= len(t):
            args.append(t[last:len(t)])

        return title, args

    def render(self, writer):
        title, args = self.evaluate()
        link = args[0] if len(args) == 1 else title
        writer.write(link)
        return link

    def category(self):
        return self.category_match.search(self.text)


class TemplateP(Expression):
    def __init__(self, node):
        self.text = ''

    def render(self, writer):
        # Ignore templates
        return ''

    # def value(self):
    #     return ''


class CommentP(Expression):
    def __init__(self, node):
        self.text = node.text
        super().__init__(node)

    def render(self, writer):
        # Ignore comments
        return ''

    # def value(self):
    #     return ''


class FormattingP(Expression):
    def __init__(self, node):
        super().__init__(node)

    def render(self, writer):
        return ''


class LinkNode(Node):
    # https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking
    media = re.compile('^(File:|Image:)')

    def __init__(self, value):
        self.text = value.text
        super().__init__(value)

    def is_media(self):
        return self.media.match(self.text)

    def compile(self, writer, parser):
        if not self.is_media():
            parser.notify(self)
            self.value.render(writer)


class HeadingNode(Node):
    def __init__(self, value):
        super().__init__(value)

    def compile(self, writer, parser):
        parser.notify(self)
        writer.write('\n\n')
        for i in self.children:
            i.value.render(writer)
        writer.write('\n\n')


# class ListItem
class ListNode(Node):
    def __init__(self, value):
        super().__init__(value)

    def compile(self, writer, parser):
        for node in self.children:
            if isinstance(node, ListNode):
                writer.write('\t'.expandtabs(1))
                node.compile(writer, parser)
            else:
                writer.write('•')
                node.compile(writer, parser)
                # written = node.value.render(writer)
                # if len(written.strip()) == 0:
                #     writer.truncate(len(writer.getvalue()) - 1)
                # else:
                writer.write('\n')
