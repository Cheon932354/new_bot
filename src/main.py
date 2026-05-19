import os
import json
import time
import requests

from collector import collect_news
from summarizer import summarize


# =========================
# Telegram 설정
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE = f"https://api.telegram.org/bot{TOKEN}"


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

    r = requests.post(BASE + "/sendMessage", json=data)

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
        c = detect_country(n["title"] + n["summary"])
        grouped.setdefault(c, []).append(n)

    return grouped


# =========================
# UI 키보드 생성
# =========================
def build_keyboard(grouped):

    keyboard = []

    for k, v in grouped.items():
        keyboard.append([{
            "text": f"{k} ({len(v)})",
            "callback_data": f"RUN|{k}"
        }])

    keyboard.append([{
        "text": "❌ 종료",
        "callback_data": "EXIT"
    }])

    return json.dumps({"inline_keyboard": keyboard})


# =========================
# 브리핑 실행 (핵심 UX)
# =========================
def run_country(country, articles):

    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    time.sleep(0.5)

    edit_message(msg_id, f"📥 기사 {len(articles)}개 확인 완료")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    for i, a in enumerate(articles):

        edit_message(
            msg_id,
            f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}"
        )

        try:
            summary = summarize(a["title"] + " " + a["summary"])
        except Exception as e:
            summary = f"❌ 요약 실패: {e}"

        result += f"""
📰 {a['title']}

{summary}

🔗 {a['link']}
-----------------------
"""

        time.sleep(0.8)

    edit_message(msg_id, "✅ 요약 완료!")

    send_message(result)


# =========================
# callback 처리
# =========================
def handle_callback(data):

    if data == "EXIT":
        send_message("❌ 종료되었습니다.")
        return

    if data.startswith("RUN|"):

        country = data.split("|")[1]

        news = collect_news()
        grouped = group_news(news)

        articles = grouped.get(country, [])

        run_country(country, articles)


# =========================
# Telegram polling (핵심)
# =========================
def listen_callbacks():

    last_update_id = None

    while True:

        url = f"{BASE}/getUpdates"

        if last_update_id:
            url += f"?offset={last_update_id + 1}"

        try:
            res = requests.get(url).json()

            for update in res.get("result", []):

                last_update_id = update["update_id"]

                if "callback_query" in update:

                    data = update["callback_query"]["data"]

                    handle_callback(data)

        except Exception as e:
            print("polling error:", e)

        time.sleep(1)


# =========================
# MAIN 실행
# =========================
def main():

    news = collect_news()
    grouped = group_news(news)

    keyboard = build_keyboard(grouped)

    send_message(
        "🌍 국가를 선택하세요",
        reply_markup=keyboard
    )

    print("UI sent")

    listen_callbacks()


# =========================
if __name__ == "__main__":
    main()