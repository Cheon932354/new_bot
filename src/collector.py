# =========================
# src/collector.py
# 가장 추천하는 최종 구조
# =========================

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
    # 아시아 전문
    # =========================
    "The Diplomat":
    "https://thediplomat.com/category/asia-defense/feed/",

    "Indian Defense News":
    "https://www.indiandefensenews.in/feeds/posts/default?alt=rss",

    "Livefist":
    "https://www.livefistdefence.com/feed",

    # =========================
    # 중남미 전문
    # =========================
    "Infodefensa":
    "https://www.infodefensa.com/rss",

    "MercoPress":
    "https://en.mercopress.com/rss",

    # ==================================================
    # 브라질
    # ==================================================
    "Brazil Defense":
    "https://news.google.com/rss/search?q=Brazil+defense",

    "Brazil Military":
    "https://news.google.com/rss/search?q=Brazil+military",

    "Brazil Defense Industry":
    "https://news.google.com/rss/search?q=Brazil+defense+industry",

    "Brazil Navy":
    "https://news.google.com/rss/search?q=Brazil+navy",

    "Brazil Army":
    "https://news.google.com/rss/search?q=Brazil+army",

    "Brazil Air Force":
    "https://news.google.com/rss/search?q=Brazil+air+force",

    # ==================================================
    # 인도
    # ==================================================
    "India Defense":
    "https://news.google.com/rss/search?q=India+defense",

    "India Military":
    "https://news.google.com/rss/search?q=India+military",

    "India Navy":
    "https://news.google.com/rss/search?q=India+navy",

    # ==================================================
    # 일본
    # ==================================================
    "Japan Defense":
    "https://news.google.com/rss/search?q=Japan+defense",

    "Japan Military":
    "https://news.google.com/rss/search?q=Japan+military",

    # ==================================================
    # 필리핀
    # ==================================================
    "Philippines Defense":
    "https://news.google.com/rss/search?q=Philippines+defense",

    "Philippines Military":
    "https://news.google.com/rss/search?q=Philippines+military",

    "Philippines Navy":
    "https://news.google.com/rss/search?q=Philippines+navy",

    # ==================================================
    # 인도네시아
    # ==================================================
    "Indonesia Defense":
    "https://news.google.com/rss/search?q=Indonesia+defense",

    "Indonesia Military":
    "https://news.google.com/rss/search?q=Indonesia+military",

    # ==================================================
    # 태국
    # ==================================================
    "Thailand Defense":
    "https://news.google.com/rss/search?q=Thailand+defense",

    "Thailand Military":
    "https://news.google.com/rss/search?q=Thailand+military",

    # ==================================================
    # 베트남
    # ==================================================
    "Vietnam Defense":
    "https://news.google.com/rss/search?q=Vietnam+defense",

    "Vietnam Military":
    "https://news.google.com/rss/search?q=Vietnam+military",

    # ==================================================
    # 말레이시아
    # ==================================================
    "Malaysia Defense":
    "https://news.google.com/rss/search?q=Malaysia+defense",

    # ==================================================
    # 방글라데시
    # ==================================================
    "Bangladesh Defense":
    "https://news.google.com/rss/search?q=Bangladesh+defense",

    # ==================================================
    # 캄보디아
    # ==================================================
    "Cambodia Defense":
    "https://news.google.com/rss/search?q=Cambodia+defense",

    "Cambodia Military":
    "https://news.google.com/rss/search?q=Cambodia+military",

    # ==================================================
    # 페루
    # ==================================================
    "Peru Defense":
    "https://news.google.com/rss/search?q=Peru+defense",

    # ==================================================
    # 칠레
    # ==================================================
    "Chile Defense":
    "https://news.google.com/rss/search?q=Chile+defense",

    # ==================================================
    # 콜롬비아
    # ==================================================
    "Colombia Defense":
    "https://news.google.com/rss/search?q=Colombia+defense",

    # ==================================================
    # 아르헨티나
    # ==================================================
    "Argentina Defense":
    "https://news.google.com/rss/search?q=Argentina+defense",

    # ==================================================
    # 우루과이
    # ==================================================
    "Uruguay Defense":
    "https://news.google.com/rss/search?q=Uruguay+defense",

    # ==================================================
    # 에콰도르
    # ==================================================
    "Ecuador Defense":
    "https://news.google.com/rss/search?q=Ecuador+defense",

    # ==================================================
    # 멕시코
    # ==================================================
    "Mexico Defense":
    "https://news.google.com/rss/search?q=Mexico+defense",

    "Mexico Military":
    "https://news.google.com/rss/search?q=Mexico+military",

    # ==================================================
    # 중앙아시아
    # ==================================================
    "Kazakhstan Military":
    "https://news.google.com/rss/search?q=Kazakhstan+military",

    "Uzbekistan Military":
    "https://news.google.com/rss/search?q=Uzbekistan+military",

    "Kyrgyzstan Military":
    "https://news.google.com/rss/search?q=Kyrgyzstan+military",

    # ==================================================
    # 국내
    # ==================================================
    "연합뉴스 정치":
    "https://www.yna.co.kr/rss/politics.xml",

    "국방일보":
    "https://kookbang.dema.mil.kr/rss.xml",

    "디펜스타임즈":
    "http://www.defensetimes.kr/rss/allArticle.xml",
}


# =========================
# 날짜 검사
# =========================

def is_recent_news(published):

    # 날짜 없으면 제외
    if not published:
        return False

    try:

        article_time = parsedate_to_datetime(
            published
        )

        now = datetime.now(
            article_time.tzinfo
        )

        diff = now - article_time

        # 미래 날짜 제거
        if diff.total_seconds() < 0:
            return False

        # 최근 72시간
        return diff <= timedelta(
            hours=72
        )

    except Exception as e:

        print(
            "날짜 파싱 실패:",
            published
        )

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
        ":",
        ",",

        "breaking:",
        "exclusive:"
    ]

    for word in remove_words:

        title = title.replace(
            word,
            " "
        )

    title = " ".join(
        title.split()
    )

    return title.strip()


# =========================
# 뉴스 수집
# =========================

def collect_news():

    news_list = []

    seen_titles = set()
    seen_links = set()

    for source, url in RSS_FEEDS.items():

        print(
            f"\n📡 수집 중: {source}"
        )

        try:

            feed = feedparser.parse(
                url
            )

            entries = feed.entries[:50]

            for entry in entries:

                title = (
                    entry.get(
                        "title",
                        ""
                    )
                )

                link = (
                    entry.get(
                        "link",
                        ""
                    )
                )

                summary = (

                    entry.get(
                        "summary",
                        ""
                    )

                    or

                    entry.get(
                        "description",
                        ""
                    )
                )

                published = (

                    entry.get(
                        "published",
                        ""
                    )

                    or

                    entry.get(
                        "updated",
                        ""
                    )

                    or

                    entry.get(
                        "pubDate",
                        ""
                    )
                )

                # =====================
                # 날짜 필터
                # =====================

                if not is_recent_news(
                    published
                ):
                    continue

                # =====================
                # 중복 제거
                # =====================

                normalized_title = (
                    normalize_title(
                        title
                    )
                )

                normalized_link = (
                    link.split("?")[0]
                )

                if (
                    normalized_title
                    in seen_titles
                ):
                    continue

                if (
                    normalized_link
                    in seen_links
                ):
                    continue

                article = {

                    "source":
                    source,

                    "title":
                    title,

                    "summary":
                    summary,

                    "link":
                    link,

                    "published":
                    published
                }

                news_list.append(
                    article
                )

                seen_titles.add(
                    normalized_title
                )

                seen_links.add(
                    normalized_link
                )

                print(
                    "✅",
                    title[:80]
                )

        except Exception as e:

            print(
                f"❌ RSS ERROR "
                f"({source})"
            )

            print(e)

    print(
        f"\n📰 최종 기사 수: "
        f"{len(news_list)}"
    )

    return news_list