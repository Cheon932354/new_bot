import os
import json
import requests

from collector import collect_news
from summarizer import summarize


# =========================
# TELEGRAM 기본 설정
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# 메시지 전송
# =========================
def send_message(text, reply_markup=None):

    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(BASE_URL + "/sendMessage", json=data)


# =========================
# 메시지 수정 (진행상황 표시)
# =========================
def edit_message(message_id, text):

    data = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": text
    }

    requests.post(BASE_URL + "/editMessageText", json=data)


# =========================
# 국가 분류
# =========================
def detect_country(text):

    t = text.lower()

    # ===== ASIA =====
    if "philippines" in t:
        return "🇵🇭 필리핀"
    if "japan" in t:
        return "🇯🇵 일본"
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

    # ===== LATAM =====
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

        country = detect_country(n["title"] + n["summary"])

        if country not in grouped:
            grouped[country] = []

        grouped[country].append(n)

    return grouped


# =========================
# 버튼 UI 생성
# =========================
def build_keyboard(grouped):

    order = [
        # Asia
        "🇵🇭 필리핀",
        "🇯🇵 일본",
        "🇮🇩 인도네시아",
        "🇲🇾 말레이시아",
        "🇻🇳 베트남",
        "🇹🇭 태국",
        "🇧🇩 방글라데시",

        # LATAM
        "🇵🇪 페루",
        "🇨🇱 칠레",
        "🇨🇴 콜롬비아",
        "🇦🇷 아르헨티나",
        "🇲🇽 멕시코",
        "🇧🇷 브라질",

        "🌍 기타"
    ]

    keyboard = []

    for c in order:

        if c in grouped:
            count = len(grouped[c])

            keyboard.append([{
                "text": f"{c} ({count})",
                "callback_data": c
            }])

    keyboard.append([{
        "text": "❌ 종료",
        "callback_data": "exit"
    }])

    return json.dumps({"inline_keyboard": keyboard})


# =========================
# 국가 브리핑 실행
# =========================
def run_country(country, articles, message_id):

    edit_message(message_id, f"📡 {country} 요약 중... ({len(articles)}개)")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    for i, a in enumerate(articles):

        edit_message(message_id, f"⏳ 진행중... {i+1}/{len(articles)}")

        summary = summarize(a["title"] + " " + a["summary"])

        result += f"""
📰 {a['title']}

{summary}

🔗 {a['link']}
------------------
"""

    send_message(result)

    # 다음 선택 UI
    send_message(
        "다음 선택:",
        reply_markup=json.dumps({
            "inline_keyboard": [
                [{"text": "🌍 다시 선택", "callback_data": "menu"}],
                [{"text": "❌ 종료", "callback_data": "exit"}]
            ]
        })
    )


# =========================
# MAIN 실행
# =========================
def main():

    print("🚀 Starting Defense Briefing Bot")

    news = collect_news()

    if not news:
        print("❌ 뉴스 없음")
        return

    grouped = group_news(news)

    keyboard = build_keyboard(grouped)

    # 첫 메시지
    send_message(
        "🌍 국가를 선택하세요:",
        reply_markup=keyboard
    )

    print("✅ UI 전송 완료")

    # ⚠️ 여기까지가 “1차 실행”
    # callback 처리까지 하려면 webhook 필요


if __name__ == "__main__":
    main()