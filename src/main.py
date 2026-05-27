import os
import requests
from datetime import datetime

from collector import collect_news
from summarizer import summarize, translate_title


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# SEND MESSAGE
# =========================
def send_message(text):

    requests.post(
        BASE + "/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
    )


# =========================
# DATE
# =========================
def get_date():
    return datetime.now().strftime("%Y-%m-%d")


# =========================
# 국내 대외협력 키워드
# =========================
EXPORT_KEYWORDS = [
    "브라질",
    "인도",
    "필리핀",
    "인도네시아",
    "페루",
    "칠레",
    "콜롬비아",
    "아르헨티나",
    "멕시코",
    "말레이시아",
    "태국",
    "베트남",
    "방글라데시",
    "우즈베키스탄",
    "카자흐스탄",
    "키르기스스탄"
]


# =========================
# COUNTRY DETECT
# =========================
def detect_country(text):

    t = (text or "").lower()

    mapping = {

        "japan":"🇯🇵 일본",
        "philippines":"🇵🇭 필리핀",
        "indonesia":"🇮🇩 인도네시아",
        "malaysia":"🇲🇾 말레이시아",
        "vietnam":"🇻🇳 베트남",
        "thailand":"🇹🇭 태국",
        "bangladesh":"🇧🇩 방글라데시",
        "india":"🇮🇳 인도",

        "uzbekistan":"🇺🇿 우즈베키스탄",
        "kazakhstan":"🇰🇿 카자흐스탄",
        "kyrgyzstan":"🇰🇬 키르기스스탄",

        "peru":"🇵🇪 페루",
        "chile":"🇨🇱 칠레",
        "colombia":"🇨🇴 콜롬비아",
        "argentina":"🇦🇷 아르헨티나",
        "mexico":"🇲🇽 멕시코",
        "brazil":"🇧🇷 브라질",
    }

    for k, v in mapping.items():
        if k in t:
            return v

    return "🌍 기타 국가"


# =========================
# 국내 대외협력 기사 판단
# =========================
def is_korean_export_news(article):

    source = article.get("source", "")

    korean_sources = [
        "연합뉴스 정치",
        "국방일보",
        "디펜스타임즈"
    ]

    if source not in korean_sources:
        return False

    text = (
        article.get("title", "")
        + " "
        + article.get("summary", "")
    )

    for keyword in EXPORT_KEYWORDS:
        if keyword in text:
            return True

    return False


# =========================
# GROUP NEWS
# =========================
def group_news(news):

    domestic_export = []

    foreign = {}

    for n in news:

        # 국내 대외협력
        if is_korean_export_news(n):
            domestic_export.append(n)
            continue

        title = n.get("title", "")
        summary = n.get("summary", "")

        country = detect_country(title + summary)

        foreign.setdefault(country, [])
        foreign[country].append(n)

    return domestic_export, foreign


# =========================
# COUNT MESSAGE
# =========================
def build_count_message(domestic_export, foreign):

    date = get_date()

    msg = f"📊 <b>방산 뉴스 업데이트 ({date})</b>\n\n"

    msg += "━━━━━━━━━━━━━━━\n"
    msg += "🇰🇷 <b>국내 방산 대외협력</b>\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    msg += f"🇰🇷 한국 : {len(domestic_export)}건\n\n"

    msg += "━━━━━━━━━━━━━━━\n"
    msg += "🌏 <b>해외 방산 뉴스</b>\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    for country, articles in foreign.items():
        msg += f"{country} : {len(articles)}건\n"

    return msg


# =========================
# BUILD MESSAGE
# =========================
def build_message(title_text, articles):

    msg = f"━━━━━━━━━━━━━━━\n"
    msg += f"{title_text}\n\n"

    for a in articles[:5]:

        title = a.get("title", "")
        summary_raw = a.get("summary", "")
        link = a.get("link", "")

        published = (
            a.get("published")
            or ""
        )

        if published:
            published = str(published)[:10]
            title_line = f"{title} ({published})"
        else:
            title_line = title

        translated_title = translate_title(title)
        summary = summarize(summary_raw)

        msg += f"""
📰 <b>원문 제목</b>
{title_line}

🇰🇷 <b>한글 제목</b>
{translated_title}

📌 <b>3줄 요약</b>
{summary}

🔗 <a href="{link}">기사 보기</a>

────────────────
"""

    return msg


# =========================
# MAIN
# =========================
def main():

    news = collect_news()

    domestic_export, foreign = group_news(news)

    # 모든 요약 먼저 완료
    domestic_msg = None

    if domestic_export:
        domestic_msg = build_message(
            "🇰🇷 <b>국내 방산 대외협력 브리핑</b>",
            domestic_export
        )

    foreign_msgs = []

    for country, articles in foreign.items():

        msg = build_message(
            f"🌏 <b>{country} 방산 브리핑</b>",
            articles
        )

        foreign_msgs.append(msg)

    # =========================
    # 메시지 전송
    # =========================
    send_message(
        build_count_message(
            domestic_export,
            foreign
        )
    )

    # 국내
    if domestic_msg:
        send_message(domestic_msg)

    # 해외
    for msg in foreign_msgs:
        send_message(msg)

    send_message(
        "✅ <b>일일 방산 브리핑 종료</b>"
    )


if __name__ == "__main__":
    main()