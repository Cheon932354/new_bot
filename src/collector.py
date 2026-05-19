import feedparser
from datetime import datetime, timedelta
import time

COUNTRY_FEEDS = {

    "브라질": [
        "https://www.defesaaereanaval.com.br/feed",
    ],

    "칠레": [
        "https://www.infodefensa.com/texto-diario/mostrar/feeds"
    ],

    "페루": [
        "https://www.infodefensa.com/peru/rss"
    ],

    "콜롬비아": [
        "https://www.infodefensa.com/colombia/rss"
    ],

    "아르헨티나": [
        "https://www.infodefensa.com/argentina/rss"
    ],

    "베트남": [
        "https://vietnamdefence.com/feed"
    ],

    "인도네시아": [
        "https://www.janes.com/feeds/news"
    ],

    "인도": [
        "https://www.indiandefensenews.in/feeds/posts/default"
    ],

    "필리핀": [
        "https://www.pna.gov.ph/rss"
    ],

    "태국": [
        "https://www.bangkokpost.com/rss/data/world.xml"
    ]
}

def collect_news():

    articles = []

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    for country, feeds in COUNTRY_FEEDS.items():

        for url in feeds:

            try:

                feed = feedparser.parse(url)

                for entry in feed.entries[:10]:

                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    link = entry.get("link", "")

                    published = None

                    if "published_parsed" in entry:

                        published = datetime.fromtimestamp(
                            time.mktime(
                                entry.published_parsed
                            )
                        )

                    # 최근 7일
                    if published and published < seven_days_ago:
                        continue

                    articles.append({
                        "country": country,
                        "title": title,
                        "summary": summary,
                        "link": link
                    })

            except Exception as e:

                print(f"RSS 오류: {url}")
                print(e)

    return articles