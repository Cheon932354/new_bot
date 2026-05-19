import feedparser
from datetime import datetime, timedelta
import time

# 국가별 현지 RSS
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

    "인도": [
        "https://www.indiandefensenews.in/feeds/posts/default"
    ]
}

# 글로벌 방산 RSS
GLOBAL_FEEDS = [

    "https://www.defensenews.com/arc/outboundfeeds/rss/",

    "https://breakingdefense.com/feed/",

    "https://www.navalnews.com/feed/"
]

# 방산 키워드
DEFENSE_KEYWORDS = [

    # 영어
    "navy",
    "air force",
    "army",
    "defense",
    "military",
    "missile",
    "fighter",
    "frigate",
    "submarine",
    "tank",
    "weapon",
    "drone",
    "radar",
    "artillery",
    "warship",
    "destroyer",
    "marine",

    # 스페인어
    "defensa",
    "armada",
    "militar",
    "fragata",
    "submarino",
    "misil",

    # 포르투갈어
    "defesa",
    "marinha",
    "fragata",
    "submarino",
    "missil"
]

# 국가/기업 키워드
COUNTRY_KEYWORDS = [

    # 국가
    "brazil",
    "chile",
    "peru",
    "ecuador",
    "colombia",
    "argentina",

    "vietnam",
    "thailand",
    "philippines",
    "indonesia",
    "india",

    # 기업/기관
    "embraer",
    "asmar",
    "cotecmar",
    "pt pal",
    "hal",
    "drdo",
    "hanwha",
    "hyundai rotem",
    "lig nex1",
    "kai"
]

def is_defense_news(text):

    text = text.lower()

    for keyword in DEFENSE_KEYWORDS:

        if keyword in text:
            return True

    return False

def contains_country_keyword(text):

    text = text.lower()

    for keyword in COUNTRY_KEYWORDS:

        if keyword in text:
            return True

    return False

def collect_news():

    articles = []

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    # =========================
    # 국가별 RSS
    # =========================

    for country, feeds in COUNTRY_FEEDS.items():

        for url in feeds:

            try:

                feed = feedparser.parse(url)

                for entry in feed.entries[:15]:

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

                    combined_text = (
                        title + " " + summary
                    )

                    # 방산뉴스 필터
                    if not is_defense_news(
                        combined_text
                    ):
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

    # =========================
    # 글로벌 RSS
    # =========================

    for url in GLOBAL_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:

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

                combined_text = (
                    title + " " + summary
                )

                # 방산 필터
                if not is_defense_news(
                    combined_text
                ):
                    continue

                # 국가/기업 필터
                if not contains_country_keyword(
                    combined_text
                ):
                    continue

                articles.append({
                    "country": "글로벌",
                    "title": title,
                    "summary": summary,
                    "link": link
                })

        except Exception as e:

            print(f"글로벌 RSS 오류: {url}")
            print(e)

    return articles