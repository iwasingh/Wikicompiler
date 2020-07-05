from config import TEST_DATA
import parser.parser as p
import compiler as c
import lexer.lexer as l
from parser.grammar import Grammar
import time


def test_parse():
    with (TEST_DATA / 'wikitext').open(encoding="utf8") as f:
        text = f.read()
        parser = p.Parser()
        ast = parser.parse(text)
        print(ast)


def test_headings():
    txt = """==History==
    """
    parser = p.Parser()
    ast = parser.parse(txt)
    # assert isinstance(ast.children[0].value,)


def test_compile():
    with (TEST_DATA / 'wikitext').open(encoding="utf8") as f:
        w_compiler = c.Compiler()
        text = f.read()
        print(w_compiler.compile(text))


def test_parse_list():
    text = """
* asd
** asd
"""
    lexer = l.Lexer()
    print(lexer.tokenize(text))
    parser = p.Parser()
    ast = parser.parse(text)
    print(ast, '\n', type(ast.children[1].children[0]))
    assert isinstance(ast.children[0].value, p.LineBreakP) \
           and isinstance(ast.children[1], p.ListNode) \
           and isinstance(ast.children[1].children[0], p.Node)

# def test_formatting():
#     txt = """'''History'''
#     ''[[Formation (1985–1987)]]''
#     Dream Theater was formed in Massachusetts in 1985 when guitarist John Petrucci, bassist John Myung, and drummer Mike Portnoy decided to form a band while attending the Berklee College of Music. The trio started by covering [[Rush (band)|Rush]] and [[Iron Maiden]] songs in the rehearsal rooms at Berklee.
#     """
#
#     parser = p.Parser()
#     ast = parser.parse(txt)
#     assert isinstance(ast.children[0].value, p.FormattingP) and ast.children[0].value.expression.text == 'History'
