import feedparser
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


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

    "Google Japan Defense":
    "https://news.google.com/rss/search?q=Japan+defense",

    "Google Thailand Defense":
    "https://news.google.com/rss/search?q=Thailand+military",

    "Google Vietnam Defense":
    "https://news.google.com/rss/search?q=Vietnam+defense",

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
# 최근 24시간 기사
# =========================
def is_recent_news(published):

    if not published:
        return False

    try:

        article_time = parsedate_to_datetime(published)

        now = datetime.utcnow(
            tzinfo=article_time.tzinfo
        )

        diff = now - article_time

        return diff <= timedelta(days=1)

    except Exception:
        return False


# =========================
# 중복 제거용 제목 정리
# =========================
def normalize_title(title):

    if not title:
        return ""

    title = title.lower()

    remove_words = [
        "[updated]",
        "(updated)",
        "|",
        "-",
        ":"
    ]

    for w in remove_words:
        title = title.replace(w, " ")

    title = " ".join(title.split())

    return title.strip()


# =========================
# NEWS COLLECTOR
# =========================
def collect_news():

    news_list = []

    # 중복 제거용
    seen_titles = set()
    seen_links = set()

    for source, url in RSS_FEEDS.items():

        print(f"수집 중: {source}")

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:

                title = entry.get("title", "")
                link = entry.get("link", "")

                normalized = normalize_title(title)

                # =========================
                # 링크 중복 제거
                # =========================
                if link in seen_links:
                    continue

                # =========================
                # 제목 중복 제거
                # =========================
                if normalized in seen_titles:
                    continue

                published = (
                    entry.get("published", "")
                    or entry.get("updated", "")
                    or entry.get("pubDate", "")
                )

                # =========================
                # 하루 이내 기사만
                # =========================
                if not is_recent_news(published):
                    continue

                summary = (
                    entry.get("summary", "")
                    or entry.get("description", "")
                )

                news = {

                    "source": source,

                    "title": title,

                    "summary": summary,

                    "link": link,

                    "published": published
                }

                news_list.append(news)

                seen_titles.add(normalized)
                seen_links.add(link)

        except Exception as e:
            print(f"RSS ERROR ({source}):", e)

    print(f"최종 기사 수: {len(news_list)}")

    return news_list