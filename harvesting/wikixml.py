import xml.sax as sax

import mwparserfromhell

from link_checker import check_link

MAX_ARTICLES = -1


class ArticleHandler(sax.ContentHandler):
    
    def __init__(self, origin_wiki, out_path, session, titles = None):
        self.title = ''
        self.wikicode = ''
        self.currentTag = ''
        self.inPage = ''
        self.origin_wiki = origin_wiki
        self.session = session
        self.count = 0
        self.finished = False
        self.titles = titles
        self.file = open(out_path, 'w')
    
    def startElement(self, tag, attributes):
        if tag == 'page':
            self.inPage = True
        self.currentTag = tag
    
    def endElement(self, tag):
        self.currentTag = ''
        if tag == 'page':
            self.parsePage(self.title, self.wikicode)
            self.inPage = False
            self.title = ''
            self.wikicode = ''
    
    def characters(self, content):
        if self.inPage and self.currentTag == 'title':
            self.title = self.title + content
        elif self.inPage and self.currentTag == 'text':
            self.wikicode = self.wikicode + content
    
    def parsePage(self, title, wikicode):
        if self.finished:
            return
        if self.titles is not None:
            # List of titles provided, check if included
            if title not in self.titles:
                return
            else:
                linked_destination = self.titles[title]
        else:
            # List of titles not provided, check if linked to the destination Wiki
            linked_destination = check_link(title, self.origin_wiki, self.session)
            if not linked_destination:
                return
        parsed_wikicode = mwparserfromhell.parse(wikicode)
        text_content = parsed_wikicode.strip_code()
        normalized_text_content = self.normalize(text_content)
        self.file.write(title + '\t' + linked_destination + '\t' + normalized_text_content + '\n')
        self.count += 1
        if self.count % 100 == 0:
            print(self.count)
        if self.count == MAX_ARTICLES:
            self.finished = True
    
    def normalize(self, text_content):
        return text_content.replace('\n', '\\n').replace('\t', '\\t')
    
    def close(self):
        self.file.close()
