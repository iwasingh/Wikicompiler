from config import TEST_DATA
import parser.parser as p
import compiler as c
import traceback


def extract_text():
    with (TEST_DATA / 'wikitext_anarchism').open(encoding="utf8") as f:
        parser = p.Parser()
        w_compiler = c.Compiler()
        text = f.read()
        try:

            # ast = parser.parse(text)
            text = w_compiler.compile(text)
            print(text)
            # print(ast)
        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':
    extract_text()
