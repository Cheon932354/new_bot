import os
import json
import time
import requests

from collector import collect_news
from summarizer import summarize


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# Telegram 기본 함수
# =========================
def send_message(text, reply_markup=None):

    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    r = requests.post(BASE + "/sendMessage", json=data)

    return r.json()["result"]["message_id"]


def edit_message(message_id, text):

    data = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": text
    }

    requests.post(BASE + "/editMessageText", json=data)


# =========================
# 국가 분류
# =========================
def detect_country(text):

    t = text.lower()

    if "japan" in t:
        return "🇯🇵 일본"
    if "philippines" in t:
        return "🇵🇭 필리핀"
    if "indonesia" in t:
        return "🇮🇩 인도네시아"
    if "malaysia" in t:
        return "🇲🇾 말레이시아"
    if "vietnam" in t:
        return "🇻🇳 베트남"
    if "thailand" in t:
        return "🇹🇭 태국"
    if "bangladesh" in t:
        return "🇧🇩 방글라데시"

    if "peru" in t:
        return "🇵🇪 페루"
    if "chile" in t:
        return "🇨🇱 칠레"
    if "colombia" in t:
        return "🇨🇴 콜롬비아"
    if "argentina" in t:
        return "🇦🇷 아르헨티나"
    if "mexico" in t:
        return "🇲🇽 멕시코"
    if "brazil" in t:
        return "🇧🇷 브라질"

    return "🌍 기타"


# =========================
# 뉴스 그룹핑
# =========================
def group_news(news_list):

    grouped = {}

    for n in news_list:
        c = detect_country(n["title"] + n["summary"])
        grouped.setdefault(c, []).append(n)

    return grouped


# =========================
# 🔥 핵심: 진행상황 포함 브리핑
# =========================
def run_country(country, articles):

    # 1️⃣ 시작 메시지
    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    time.sleep(0.5)

    edit_message(msg_id, f"📥 기사 {len(articles)}개 분석 준비 완료")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    # 2️⃣ 요약 진행 루프
    for i, a in enumerate(articles):

        # ⏳ 진행 상태 표시 (핵심)
        edit_message(
            msg_id,
            f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}"
        )

        try:
            summary = summarize(a["title"] + " " + a["summary"])
        except Exception as e:
            summary = f"❌ 요약 실패: {str(e)}"

        result += f"""
📰 {a['title']}

{summary}

🔗 {a['link']}
-----------------------
"""

        # ⭐ Telegram rate limit 방지 (중요)
        time.sleep(0.8)

    # 3️⃣ 완료 상태
    edit_message(msg_id, "✅ 요약 완료!")

    time.sleep(0.5)

    send_message(result)

    send_message("➡ 다른 국가를 선택하거나 종료하세요")


# =========================
# MAIN
# =========================
def main():

    news = collect_news()

    grouped = group_news(news)

    keyboard = []

    for k, v in grouped.items():
        keyboard.append([{
            "text": f"{k} ({len(v)})",
            "callback_data": k
        }])

    keyboard.append([{
        "text": "❌ 종료",
        "callback_data": "exit"
    }])

    send_message(
        "🌍 국가를 선택하세요",
        reply_markup=json.dumps({"inline_keyboard": keyboard})
    )

    print("UI 전송 완료")


if __name__ == "__main__":
    main()