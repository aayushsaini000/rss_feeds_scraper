import feedparser
from app.models import RssFeed
from app import db
from datetime import datetime

def getRssFeed(query):
    output = []
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    res = feedparser.parse(url)
    if res.get('entries'):
        for entry in res.entries:
            item = {
                'search_text': query.lower(),
                'link': entry.link,
                'title': entry.title,
                'description': entry.description,
                'published': entry.published,
                'gid': entry.id,
                'datetime': entry.published
            }
            output.append(item)
        filtered_feed = filterExistedFeed(output)
        if filtered_feed:
            return {'data': filtered_feed}
        return {'data': [], 'message': 'No new feeds found.'}    
    return {'data': [], 'message': 'No feeds found.'}


def filterExistedFeed(feeds):
    dt_format = '%a, %d %b %Y %H:%M:%S GMT'
    filtered_feed = []
    for dict_obj in feeds:
        row = RssFeed.query.filter_by(gid=dict_obj['gid']).first()
        if row is None:
            dict_obj['datetime'] = datetime.strptime(dict_obj['datetime'], dt_format)
            filtered_feed.append(dict_obj)
            print('\n')
    return filtered_feed
