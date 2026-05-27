import feedparser


# =========================
# RSS FEEDS
# =========================
RSS_FEEDS = {

    # =========================
    # 글로벌 방산
    # =========================
    "Defense News":
    "https://www.defensenews.com/arc/outboundfeeds/rss/",

    "Breaking Defense":
    "https://breakingdefense.com/feed/",

    "Army Recognition":
    "https://www.armyrecognition.com/rss.xml",

    "Defense Blog":
    "https://defence-blog.com/feed/",

    "Naval News":
    "https://www.navalnews.com/feed/",

    "Defense One":
    "https://www.defenseone.com/rss/all/",

    # =========================
    # 아시아
    # =========================
    "The Diplomat":
    "https://thediplomat.com/category/asia-defense/feed/",

    "Indian Defense News":
    "https://www.indiandefensenews.in/feeds/posts/default?alt=rss",

    "Livefist":
    "https://www.livefistdefence.com/feed",

    # =========================
    # 중남미
    # =========================
    "Infodefensa":
    "https://www.infodefensa.com/rss",

    "MercoPress":
    "https://en.mercopress.com/rss",

    # =========================
    # Google News RSS
    # =========================
    "Google Brazil Defense":
    "https://news.google.com/rss/search?q=Brazil+defense",

    "Google India Defense":
    "https://news.google.com/rss/search?q=India+defense",

    "Google Philippines Defense":
    "https://news.google.com/rss/search?q=Philippines+military",

    "Google Peru Defense":
    "https://news.google.com/rss/search?q=Peru+defense",

    "Google Chile Defense":
    "https://news.google.com/rss/search?q=Chile+defense",

    "Google Indonesia Defense":
    "https://news.google.com/rss/search?q=Indonesia+military",

    # =========================
    # 국내 방산
    # =========================
    "연합뉴스 정치":
    "https://www.yna.co.kr/rss/politics.xml",

    "국방일보":
    "https://kookbang.dema.mil.kr/rss.xml",

    "디펜스타임즈":
    "http://www.defensetimes.kr/rss/allArticle.xml",
}


# =========================
# NEWS COLLECTOR
# =========================
def collect_news():

    news_list = []

    for source, url in RSS_FEEDS.items():

        print(f"수집 중: {source}")

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:15]:

                news = {

                    "source": source,

                    "title":
                    entry.get("title", ""),

                    "summary":
                    entry.get("summary", "")
                    or entry.get("description", ""),

                    "link":
                    entry.get("link", ""),

                    "published":
                    entry.get("published", "")
                    or entry.get("updated", "")
                    or entry.get("pubDate", "")
                }

                news_list.append(news)

        except Exception as e:
            print(f"RSS ERROR ({source}):", e)

    return news_list