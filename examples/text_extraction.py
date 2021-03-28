from config import ROOT
import compiler as c
import traceback

outputsDir = ROOT / 'examples/outputs'

def extract_text():
    outputFile = (outputsDir / 'wikitext_anarchism.txt').open(encoding="utf8", mode="w")
    with (ROOT / 'examples/data/wikitext_anarchism.txt').open(encoding="utf8") as f:
        w_compiler = c.Compiler()
        text = f.read()
        try:
          text = w_compiler.compile(text)
          outputFile.write(text)
        except Exception as e:
            traceback.print_exc()

    outputFile.close()	

if __name__ == '__main__':
    extract_text()
