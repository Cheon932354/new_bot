import os
import requests
from datetime import datetime

from collector import collect_news
from summarizer import summarize


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# SEND MESSAGE
# =========================
def send_message(text):

    res = requests.post(
        BASE + "/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
    )

    print("TELEGRAM:", res.status_code)


# =========================
# DATE
# =========================
def get_date():
    return datetime.now().strftime("%Y-%m-%d")


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

        "peru":"🇵🇪 페루",
        "chile":"🇨🇱 칠레",
        "colombia":"🇨🇴 콜롬비아",
        "argentina":"🇦🇷 아르헨티나",
        "mexico":"🇲🇽 멕시코",
        "brazil":"🇧🇷 브라질"
    }

    for k, v in mapping.items():
        if k in t:
            return v

    return "🌍 기타 국가"


# =========================
# GROUP
# =========================
def group_news(news):

    grouped = {}

    for n in news:

        title = n.get("title","")
        summary = n.get("summary","")

        country = detect_country(title + summary)

        grouped.setdefault(country, []).append(n)

    return grouped


# =========================
# COUNT MESSAGE
# =========================
def build_count_message(grouped):

    date = get_date()

    msg = f"📊 <b>방산 뉴스 업데이트 ({date})</b>\n\n"

    for country, articles in grouped.items():
        msg += f"{country} : {len(articles)}건\n"

    return msg


# =========================
# COUNTRY SUMMARY MESSAGE (핵심 변경)
# =========================
def build_country_message(country, articles):

    msg = f"━━━━━━━━━━━━━━━\n"
    msg += f"🇺🇳 <b>{country}</b>\n\n"

    for a in articles[:5]:

        title = a.get("title","")
        summary_raw = a.get("summary","")
        link = a.get("link","")

        published = a.get("published") or a.get("date") or a.get("pubDate") or ""

        if published:
            published = str(published)[:10]
            title_line = f"{title} ({published})"
        else:
            title_line = title

        if not title or not summary_raw:
            continue

        try:
            summary = summarize(title + " " + summary_raw)
        except:
            summary = "요약 실패"

        msg += f"""
📰 <b>{title_line}</b>

📌 <b>요약</b>
{summary}

🔗 <a href="{link}">기사 보기</a>

────────────────
"""

    return msg


# =========================
# MAIN
# =========================
def main():

    print("🚀 뉴스 수집 시작")

    news = collect_news()
    grouped = group_news(news)

    # 1️⃣ 카운트 메시지
    send_message(build_count_message(grouped))

    # 2️⃣ 나라별 개별 메시지 (핵심)
    for country, articles in grouped.items():

        if not articles:
            continue

        msg = build_country_message(country, articles)
        send_message(msg)

    print("✅ 완료")


if __name__ == "__main__":
    main()