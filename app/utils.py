import feedparser

def getRssFeedXML(url):
    d = feedparser.parse(url)
    return d
