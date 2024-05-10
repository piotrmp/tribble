import sys, pathlib
import xml.sax as sax

import requests_cache

from wikixml import ArticleHandler

origin_wiki = 'an' #'oc' 'ast'
dump_path = pathlib.Path.home() / 'data' / 'tribble' / 'wiki'/(origin_wiki + 'wiki-20240420-pages-articles.xml')
cache_path = pathlib.Path.home() / 'data' / 'tribble'/'cache'
out_path = pathlib.Path.home() / 'data' / 'tribble'/ (origin_wiki+'_text.tsv')

session = requests_cache.CachedSession(str(cache_path), backend='sqlite')

parser = sax.make_parser()
parser.setFeature(sax.handler.feature_namespaces, 0)
handler = ArticleHandler(origin_wiki, out_path, session)
parser.setContentHandler(handler)
parser.parse(dump_path)

handler.close()
session.close()