import os
import requests
from datetime import datetime

from collector import collect_news
from summarizer import summarize


# =========================
# ENV
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# TELEGRAM SEND
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
# COUNTRY DETECT (제외 국가 반영)
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
# GROUP INIT (0건 보장)
# =========================
def group_news(news):

    grouped = {
        "🇯🇵 일본": [],
        "🇵🇭 필리핀": [],
        "🇮🇩 인도네시아": [],
        "🇲🇾 말레이시아": [],
        "🇻🇳 베트남": [],
        "🇹🇭 태국": [],
        "🇧🇩 방글라데시": [],
        "🇮🇳 인도": [],

        "🇵🇪 페루": [],
        "🇨🇱 칠레": [],
        "🇨🇴 콜롬비아": [],
        "🇦🇷 아르헨티나": [],
        "🇲🇽 멕시코": [],
        "🇧🇷 브라질": [],

        "🌍 기타 국가": []
    }

    for n in news:

        title = n.get("title", "")
        summary = n.get("summary", "")

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
# SUMMARY MESSAGE (날짜 + 발행일 포함)
# =========================
def build_summary_message(grouped):

    msg = "📡 <b>방산 브리핑 리포트</b>\n"

    for country, articles in grouped.items():

        if not articles:
            continue

        msg += f"\n━━━━━━━━━━━━━━━\n"
        msg += f"🇺🇳 <b>{country}</b>\n"

        for a in articles[:5]:

            title = a.get("title", "")
            summary_raw = a.get("summary", "")
            link = a.get("link", "")

            # 🔥 발행일 통합 처리
            published = (
                a.get("published")
                or a.get("date")
                or a.get("pubDate")
                or ""
            )

            if published:
                published = str(published)[:10]
                title_line = f"{title} ({published})"
            else:
                title_line = f"{title} (No date)"

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

        msg += "\n"

    return msg


# =========================
# MAIN
# =========================
def main():

    print("🚀 뉴스 수집 시작")

    news = collect_news()

    grouped = group_news(news)

    # 🔥 모든 요약 완료 후 메시지 생성
    count_msg = build_count_message(grouped)
    summary_msg = build_summary_message(grouped)

    # 🔥 순차 전송
    send_message(count_msg)
    send_message(summary_msg)

    print("✅ 완료")


if __name__ == "__main__":
    main()