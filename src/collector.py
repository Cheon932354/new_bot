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
    # Google RSS
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
    # 국내
    # =========================
    "연합뉴스 정치":
    "https://www.yna.co.kr/rss/politics.xml",

    "국방일보":
    "https://kookbang.dema.mil.kr/rss.xml",

    "디펜스타임즈":
    "http://www.defensetimes.kr/rss/allArticle.xml",
}


# =========================
# 최근 뉴스 여부
# =========================
def is_recent_news(published):

    # 날짜 자체가 없는 RSS는 허용
    if not published:
        return True

    try:

        article_time = parsedate_to_datetime(published)

        now = datetime.utcnow(
            tzinfo=article_time.tzinfo
        )

        diff = now - article_time

        # 미래 날짜 제거
        if diff.total_seconds() < 0:
            return False

        # 최근 48시간 기사만 허용
        return diff <= timedelta(days=2)

    # 날짜 파싱 실패 시 제거
    except Exception:

        print("날짜 파싱 실패:", published)

        return False


# =========================
# 제목 정규화
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
# 뉴스 수집
# =========================
def collect_news():

    news_list = []

    # 중복 제거용
    seen_titles = set()
    seen_links = set()

    for source, url in RSS_FEEDS.items():

        print(f"\n📡 수집 중: {source}")

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:

                title = entry.get("title", "")
                link = entry.get("link", "")

                normalized = normalize_title(title)

                # =========================
                # 날짜
                # =========================
                published = (
                    entry.get("published", "")
                    or entry.get("updated", "")
                    or entry.get("pubDate", "")
                )

                # =========================
                # 최신 뉴스 필터
                # =========================
                if not is_recent_news(published):
                    continue

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

                print("✅", title)

        except Exception as e:

            print(f"❌ RSS ERROR ({source})")
            print(e)

    print(f"\n📰 최종 기사 수: {len(news_list)}")

    return news_list