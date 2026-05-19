import os
import json
import requests

from collector import collect_news
from summarizer import summarize


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# 기본 메시지 전송
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

    # ⭐ message_id 반환 (핵심)
    return r.json()["result"]["message_id"]


# =========================
# 메시지 수정 (진행상황)
# =========================
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

        country = detect_country(n["title"] + n["summary"])

        if country not in grouped:
            grouped[country] = []

        grouped[country].append(n)

    return grouped


# =========================
# 국가 브리핑 실행 (핵심)
# =========================
def run_country(country, articles):

    # 1️⃣ 초기 메시지
    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    # 2️⃣ 실제 진행 상태 업데이트
    edit_message(msg_id, f"📥 {country} 기사 {len(articles)}개 확인 완료")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    # 3️⃣ 요약 진행
    for i, a in enumerate(articles):

        edit_message(
            msg_id,
            f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}"
        )

        summary = summarize(a["title"] + " " + a["summary"])

        result += f"""
📰 {a['title']}

{summary}

🔗 {a['link']}
------------------
"""

    # 4️⃣ 완료 상태
    edit_message(msg_id, "✅ 요약 완료! 보고서 생성 중...")

    send_message(result)

    # 5️⃣ 다음 선택 UI
    send_message(
        "➡ 다음 선택",
        reply_markup=json.dumps({
            "inline_keyboard": [
                [{"text": "🌍 다른 국가 선택", "callback_data": "menu"}],
                [{"text": "❌ 종료", "callback_data": "exit"}]
            ]
        })
    )


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

    keyboard.append([{"text": "❌ 종료", "callback_data": "exit"}])

    send_message(
        "🌍 국가를 선택하세요",
        reply_markup=json.dumps({"inline_keyboard": keyboard})
    )

    print("UI sent")


if __name__ == "__main__":
    main()