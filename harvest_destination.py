import pathlib
import xml.sax as sax

from wikixml import ArticleHandler

destination_wiki = 'es'
data_path = pathlib.Path.home() / 'data' / 'tribble'
dump_path = pathlib.Path.home() / 'data' / 'tribble' / 'wiki' / (destination_wiki + 'wiki-20240420-pages-articles.xml')

titles = {}
for origin_wiki in ['an', 'oc', 'ast']:
    for line in open(data_path / (origin_wiki + '_text.tsv')):
        parts = line.split('\t')
        titles[parts[1]] = 'NA'

parser = sax.make_parser()
parser.setFeature(sax.handler.feature_namespaces, 0)
handler = ArticleHandler(origin_wiki, data_path / (destination_wiki + '_text.tsv'), None, titles=titles)
parser.setContentHandler(handler)
parser.parse(dump_path)

handler.close()
