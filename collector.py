import feedparser

RSS_FEEDS = [
    "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "https://www.navalnews.com/feed/",
    "https://breakingdefense.com/feed/"
]

def collect_news():
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary
            })

    return articles