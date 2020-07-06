import pytest
from lxml import etree
from config import DUMP_FOLDER
from compiler import Compiler
from utils.combinators import ParseError
from lexer.lexer import RedirectFound
from lexer.utils import MalformedTag
import logging

logger = logging.getLogger()


@pytest.mark.slow
def test_dump():
    directory = DUMP_FOLDER
    xml_parser = WikiXML(namespace='http://www.mediawiki.org/xml/export-0.10/')
    compiler = Compiler()
    miss = 0
    for wiki in directory.iterdir():
        if wiki.is_file() and wiki.stem.startswith('enwiki'):
            for root in xml_parser.from_xml(str(wiki)):
                listener = None
                try:
                    id, title, text = xml_parser.get(root)
                    logger.info(f'{title.text} compiling')
                    # if title.text.lower() == "athens":
                    #     logger.info(text.text)
                    article = compiler.compile(text.text)
                    logger.info(f'{title.text} compiled')
                except (ParseError, MalformedTag, RedirectFound) as e:
                    miss += 1
                    logger.info(f'{e.type}')

    if miss > 0:
        logger.warning(f'{miss} articles ignored')


class WikiXML:

    def __init__(self, namespace):
        self._prefix = 'W'
        self.TITLE = '{0}:title'.format(self._prefix)
        self.TEXT = '{0}:revision/{0}:text'.format(self._prefix)
        self.ID = '{0}:id'.format(self._prefix)

        self.namespaces = {self._prefix: namespace}
        self._base_tag = f'{{{namespace}}}' + 'page'

    def from_xml(self, path):
        context = etree.iterparse(path, events=('end',), tag=self._base_tag, huge_tree=True)
        # TODO improve with iterchildren/iterdescendants instead of xpath
        for _, root in context:
            yield root
            while root.getprevious() is not None:
                del root.getparent()[0]
            root.clear()

    def title(self, root):
        return root.xpath(self.TITLE, namespaces=self.namespaces)[0]

    def text(self, root):
        return root.xpath(self.TEXT, namespaces=self.namespaces)[0]

    def id(self, root):
        return root.xpath(self.ID, namespaces=self.namespaces)[0]

    def get(self, root):
        # TODO use a high order func
        return self.id(root), self.title(root), self.text(root)
