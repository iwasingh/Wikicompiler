import logging
import re
from enum import Enum
from lexer.symbols import Template, Link, Text, Token, Redirect, \
    Comment, IGNORED_TAGS, LineBreak, Heading, Heading4, Heading3, Heading5, Heading6, \
    Italic, ItalicAndBold, Bold, List

from .utils import RecursiveMatch, recursive

logger = logging.getLogger('lexer')


class Encoder:
    def __init__(self):
        pass

    def encode(self, text):
        return text


class Symbol(Enum):
    """
    Type of symbol
    """
    RESERVED = 'RESERVED'
    ID = 'ID'
    IGNORE = 'IGNORE'


class LexerToken(Token):
    def __init__(self, token, row, col, text=''):
        self._token = token
        self._row = row
        self._col = col
        self._text = text

        # TODO call super()

    @property
    def token(self):
        return self._token

    @property
    def text(self):
        return self._text

    def __repr__(self):
        # return self._text + '\n'
        return self.__str__()

    def __str__(self):
        return self._token.__repr__() + f' [{self._col}]'
        # return '\n' + self._text + ' ' + str(self._col)

    def __eq__(self, token):
        return self._token == token

    def __ne__(self, token):
        return not self.__eq__(token)


class EOFToken(LexerToken):
    def __init__(self, row, col):
        super().__init__(Lexer.EOF, row, col)


"""
Default global table

"""
GLOBAL_TABLE = {
    Symbol.RESERVED: [],
    Symbol.ID: [],
    Symbol.IGNORE: []
}


class Lexer:
    """
    Lexer that handles streams of character and delivers tokens
    """

    EOF = Token('EOF')

    def __init__(self, encoder=Encoder()):
        self._row = 0  # Not used yet
        self._col = 0
        self.encoder = encoder
        self.tokens = list()
        self.last_token = None
        self.table = {
            Symbol.RESERVED: [],
            Symbol.IGNORE: [],
            Symbol.ID: []
        }
        self.__create_table()

        # for index, s in enumerate(self.table[Symbol.RESERVED]):
        #     setattr(s, 'lexer', self)
        #     self.table[Symbol.RESERVED][index] = s

        # for s in self.table[Symbol.RESERVED]:
        #     # s.lexer = property(lambda _: self)
        #     setattr(s, 'lexer', self)

    def __create_table(self):
        for k, v in GLOBAL_TABLE.items():
            for symbol in v:
                inst = symbol()
                setattr(inst, 'lexer', self)
                self.table[k].append(inst)

    def _tokenize(self, text, symbol_type):
        """
        Tokenizer
        :param text:
        :param symbol_type:
        :return:
        """
        text = self.encoder.encode(text)
        tokens = []

        # Debugging
        # if symbol_type == Symbol.ID: breakpoint()
        for symbol in self.table[symbol_type]:
            # try:
            match, token = symbol.match(text, self._col)
            # Find a better way to do it
            if match:
                if isinstance(match, RecursiveMatch):
                    for (m, t) in match.matches:
                        tokens.append(
                            LexerToken(t if isinstance(t, Token) else TextT.start,
                                       self._row,
                                       self._col,
                                       m.group(0)))

                else:
                    tokens.append(LexerToken(token, self._row, self._col, match.group(0)))

                self._col = match.end(0)
            # except MalformedTag as e:

        if len(tokens) == 0 and symbol_type == Symbol.ID:
            self._col += 1

        if self._col >= len(text):
            return tokens, None

        return tokens, Symbol.RESERVED if len(tokens) > 0 else Symbol.ID

    def tokenize(self, text):
        self.tokens = list()
        self.last_token = None
        self._col = 0
        symbol_type = Symbol.RESERVED

        while self._col < len(text):
            for ignore in self.table[Symbol.IGNORE]:
                match = ignore.match(text, self._col)
                if match:
                    # print(match, text[match.start(0):match.end(0)])
                    self._col = match.end(0)
            else:
                resolved_tokens, next_symbol = self._tokenize(text, symbol_type)
                symbol_type = next_symbol
                self.tokens = self.tokens + resolved_tokens
                self.last_token = self.tokens[-1] if len(self.tokens) else None
                if symbol_type is None:
                    break

        self.tokens.append(EOFToken(self._row, self._col))
        logger.info(self.tokens)
        logger.info('EOF')
        self._col += 1
        return self.tokens

    # def __new__(cls, *args, **kwargs):
    #     instance = super().__new__(cls, *args, **kwargs)
    #     print(instance)
    #     for s in Lexer.table[Symbol.RESERVED]:
    #         s.lexer = property(lambda self: instance)
    #
    #     return instance


class SymbolNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


def definition(symbol_type):
    def __wrap(symbol):
        if symbol_type in GLOBAL_TABLE:
            GLOBAL_TABLE[symbol_type].append(symbol)
        else:
            raise SymbolNotFoundError('Symbol category missing')
        return symbol
        # class Wrapper(symbol):
        #     def __init__(self):
        #         super().__init__()
        #
        # return Wrapper

    return __wrap


""" Lexer symbol definitions """


@definition(Symbol.RESERVED)
class TemplateT(Template):
    def __init__(self):
        super().__init__()

    def match(self, text, pos, **kwargs):
        return recursive(text, self.start, self.end, pos), self.start


# Lexer.symbol(Symbol.RESERVED)(Link)
@definition(Symbol.RESERVED)
class LinkT(Link):

    def __init__(self):
        super().__init__()


# Headings
definition(Symbol.RESERVED)(Heading6)
definition(Symbol.RESERVED)(Heading5)
definition(Symbol.RESERVED)(Heading4)
definition(Symbol.RESERVED)(Heading3)
definition(Symbol.RESERVED)(Heading)

# Comment
definition(Symbol.RESERVED)(Comment)


# List
# Lexer.symbol(Symbol.RESERVED)(List)

# @Lexer.symbol(Symbol.RESERVED)
# class HeadingT(Heading):
#     def match(self, text, pos, **kwargs):
#         match, token = super().match(text, pos, **kwargs)
#         if match and self.lexer.last_token is not None and self.lexer.last_token.token != LineBreak.start:
#             return match, TextT.start
#
#         return match, token

# class Lex(type):
#     def __new__(cls, *args, **kwargs):
#         cls.lexer =


@definition(Symbol.RESERVED)
class ListT(List):
    def match(self, text, pos, **kwargs):
        match, token = super().match(text, pos, **kwargs)
        if match and self.lexer.last_token \
                is not None and self.lexer.last_token.token != LineBreak.start \
                and self.lexer.last_token.token != self.start:
            return match, TextT.start

        return match, token


@definition(Symbol.RESERVED)
class RedirectT(Redirect):
    def match(self, text, pos, **kwargs):
        if self.start.match(text, pos, **kwargs):
            raise RedirectFound(text)

        return None, self.start


# Lexer.symbol(Symbol.RESERVED)(ItalicAndBold)
# Lexer.symbol(Symbol.RESERVED)(Bold)
# Lexer.symbol(Symbol.RESERVED)(Italic)

definition(Symbol.RESERVED)(LineBreak)


@definition(Symbol.IGNORE)
class IgnoreTags:
    # start = Token('MATH_JAX_START', r'<math')
    # end = Token('MATH_JAX_END', r'')
    tags = [] + IGNORED_TAGS

    def __init__(self):
        self.regex = re.compile('|'.join(self.tags), re.DOTALL)

    def match(self, text, pos, **kwargs):
        return self.regex.match(text, pos, **kwargs)


@definition(Symbol.ID)
class TextT(Text):
    # TODO Copy here the logic in the base class
    # tags = [symbol.start.regex + '|' + symbol.end.regex for symbol in Lexer.table[Symbol.RESERVED]]
    # start = Token('TEXT', '.*?(?={0})|.*'.format('|'.join(tags), re.DOTALL))
    # end = start  # None or NoneToken

    def __init__(self):
        super().__init__()


# @Lexer.symbol(Symbol.IGNORE)
class Ignore:
    def __init__(self):
        self._regex = re.compile(r'\s')

    def match(self, text, pos, **kwargs):
        return self._regex.match(text, pos)


class RedirectFound(Exception):
    def __init__(self, message=''):
        self.type = 'RedirectFound'
        self.message = f"RedirectError: Redirect article"
