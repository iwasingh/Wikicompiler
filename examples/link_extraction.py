from config import ROOT
import compiler as c
import traceback

categories = []
links = []
reverse_graph = []

outputsDir = ROOT / 'examples/outputs'

def normalize_title(title):
    return title.split('|')[0].lower().replace(" ", "_")


def parse_link(node):
    category = node.value.category()
    if category:
        categories.append(category.group())
    else:
        article_link = normalize_title(node.value.text)
        if article_link not in reverse_graph:
            reverse_graph.append(article_link)


def extract_links():
    outputFile = (outputsDir / 'wikitext_link_extraction.txt').open(encoding="utf8", mode="w")
    with (ROOT / 'examples/data/wikitext_link_extraction.txt').open(encoding="utf8") as f:
        w_compiler = c.Compiler()
        listener = w_compiler.on(lambda node: parse_link(node), c.ParseTypes.LINK)
        text = f.read()
        try:
            w_compiler.compile(text)
            outputFile.write(f'\n\n* Links\n\n {reverse_graph} \n\n* Categories\n {categories}'),
        except Exception as e:
            traceback.print_exc()
        finally:
            listener()  # free listener


if __name__ == '__main__':
    extract_links()
