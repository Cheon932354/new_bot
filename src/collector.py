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

    "defensa",
    "armada",
    "militar",
    "fragata",
    "submarino",

    "defesa",
    "marinha",
    "fragata",
    "submarino"
]

def is_defense_news(text):

    text = text.lower()

    for keyword in DEFENSE_KEYWORDS:

        if keyword in text:
            return True

    return False

# 글로벌 RSS 국가 자동분류
def detect_country(text):

    text = text.lower()

    mapping = {

        "brazil": "브라질",
        "embraer": "브라질",

        "chile": "칠레",
        "asmar": "칠레",

        "peru": "페루",

        "colombia": "콜롬비아",
        "cotecmar": "콜롬비아",

        "argentina": "아르헨티나",

        "india": "인도",
        "hal": "인도",
        "drdo": "인도",

        "indonesia": "인도네시아",
        "pt pal": "인도네시아",

        "philippines": "필리핀",

        "vietnam": "베트남",

        "thailand": "태국",

        "hanwha": "한국기업",
        "hyundai rotem": "한국기업",
        "lig nex1": "한국기업",
        "kai": "한국기업"
    }

    for keyword, country in mapping.items():

        if keyword in text:
            return country

    return None

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

                    if published and published < seven_days_ago:
                        continue

                    combined_text = (
                        title + " " + summary
                    )

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

                if published and published < seven_days_ago:
                    continue

                combined_text = (
                    title + " " + summary
                )

                if not is_defense_news(
                    combined_text
                ):
                    continue

                detected_country = detect_country(
                    combined_text
                )

                if not detected_country:
                    continue

                articles.append({
                    "country": detected_country,
                    "title": title,
                    "summary": summary,
                    "link": link
                })

        except Exception as e:

            print(f"글로벌 RSS 오류: {url}")
            print(e)

    return articles