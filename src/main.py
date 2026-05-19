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
# TELEGRAM
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
# 국가 분류
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
# 그룹핑
# =========================
def group_news(news):

    grouped = {}

    for n in news:

        title = n.get("title", "")
        summary = n.get("summary", "")

        country = detect_country(title + summary)

        grouped.setdefault(country, []).append(n)

    return grouped


# =========================
# 1차 메시지 (카운트)
# =========================
def send_count(grouped):

    msg = "📊 <b>오늘 방산 뉴스 업데이트</b>\n\n"

    for country, articles in grouped.items():
        msg += f"{country} : {len(articles)}건\n"

    send_message(msg)


# =========================
# 2차 메시지 (카드 UI)
# =========================
def send_summary(grouped):

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

            if not title or not summary_raw:
                continue

            try:
                summary = summarize(title + " " + summary_raw)
            except:
                summary = "요약 실패"

            msg += f"""
📰 <b>{title}</b>

📌 <b>요약</b>
{summary}

🔗 <a href="{link}">기사 보기</a>

────────────────
"""

        msg += "\n"

    send_message(msg)


# =========================
# MAIN JOB (GitHub Actions 실행용)
# =========================
def main():

    print("🚀 뉴스 수집 시작")

    news = collect_news()

    grouped = group_news(news)

    # =========================
    # 1️⃣ 국가별 카운트
    # =========================
    send_count(grouped)

    # =========================
    # 2️⃣ 카드형 요약
    # =========================
    send_summary(grouped)

    print("✅ 브리핑 완료")


# =========================
if __name__ == "__main__":
    main()