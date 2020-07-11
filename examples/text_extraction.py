from config import TEST_DATA
import compiler as c
import traceback


def extract_text():
    with (TEST_DATA / 'wikitext_anarchism').open(encoding="utf8") as f:
        w_compiler = c.Compiler()
        text = f.read()
        try:

            text = w_compiler.compile(text)
            print(text)
        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':
    extract_text()
