from .utils import FromFile
from ..config import TEST_DATA
import lexer.lexer as l
import lexer.utils as utils
import pytest


def test_tokenize():
    with open(TEST_DATA / 'wikitext_tokenize') as f:
        text = f.read()
        lexer = l.Lexer()
        tokens = lexer.tokenize(text)
        print(tokens)
        assert tokens[0].token == l.Template().start and tokens[len(tokens) - 2].token == l.LineBreak().start


def test_tokenize_errors():
    text = """{{Infobox"""
    lexer = l.Lexer()

    with pytest.raises(utils.MalformedTag):
        lexer.tokenize(text)


def test_comment():
    lexer = l.Lexer()
    tokens = lexer.tokenize('&lt;!-- In the interest of restricting article length, please limit this section to '
                            'two or three short paragraphs and add any substantial information to the main Issues '
                            'in anarchism article. Thank you. --&gt;')

    assert tokens[0].token == l.Comment().start


def test_redirect():
    lexer = l.Lexer()
    text = """#REDIRECT [[Ancient Greece]]{{Rcat shell|{{R move}}{{R related}}{{R unprintworthy}}}}"""
    with pytest.raises(l.RedirectFound):
        tokens = lexer.tokenize(text)


def test_newline():
    text = """Anarchism is political movement.\n"""
    lexer = l.Lexer()
    tokens = lexer.tokenize(text)
    assert tokens[len(tokens) - 2].token == l.LineBreak().start


# def test_formatting():
#     text = """To ''italicize text'', put two consecutive apostrophes on each side of it.
#     Three apostrophes each side will '''bold the text'''.
#     Five consecutive apostrophes on each side (two for italics plus three for bold) produces '''''bold italics'''''.
#     '''''Italic and bold formatting''''' works correctly only within a single line.
#     For text as {{smallcaps|small caps}}, use the template {{tl|smallcaps}}.
#     """
#     lexer = l.Lexer()
#     match = [l.Italic(), l.Bold(), l.ItalicAndBold(), l.ItalicAndBold()]
#     tokens = lexer.tokenize(text)
#     m = match.pop(0)
#     for t in tokens:
#         if t.token == m.start and len(match) > 0:
#             m = match.pop(0)
#
#     assert len(match) == 0
