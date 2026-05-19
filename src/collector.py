import feedparser
from datetime import datetime, timedelta
import time

RSS_FEEDS = [
    "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "https://www.navalnews.com/feed/",
    "https://breakingdefense.com/feed/"
]

COUNTRY_KEYWORDS = [
    "Brazil",
    "Chile",
    "Peru",
    "Ecuador",
    "Colombia",
    "Argentina",
    "Vietnam",
    "Thailand",
    "Philippines",
    "Indonesia",
    "India"
]

def collect_news():

    articles = []

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    for url in RSS_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                published = None

                if "published_parsed" in entry:

                    published = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed)
                    )

                # 최근 7일 기사만
                if published and published < seven_days_ago:
                    continue

                combined_text = (
                    title.lower() + " " + summary.lower()
                )

                matched = False

                for keyword in COUNTRY_KEYWORDS:

                    if keyword.lower() in combined_text:
                        matched = True
                        break

                if not matched:
                    continue

                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": link
                })

        except Exception as e:

            print(f"RSS 오류: {url}")
            print(e)

    return articles