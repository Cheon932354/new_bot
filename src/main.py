import os
import json
import requests

from collector import collect_news
from summarizer import summarize


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE = f"https://api.telegram.org/bot{TOKEN}"


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
    if "brazil" in t:
        return "🇧🇷 브라질"

    return "🌍 기타"


# =========================
def group(news):

    grouped = {}

    for n in news:
        c = detect_country(n["title"] + n["summary"])
        grouped.setdefault(c, []).append(n)

    return grouped


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
def main():

    news = collect_news()
    grouped = group(news)

    keyboard = build_keyboard(grouped)

    send_message(
        "🌍 국가를 선택하세요",
        reply_markup=keyboard
    )

    print("UI sent")


# =========================
# callback 처리 (핵심 추가)
# =========================
def handle_callback(data):

    if data == "EXIT":
        send_message("종료되었습니다.")
        return

    if data.startswith("RUN|"):

        country = data.split("|")[1]

        news = collect_news()
        grouped = group(news)

        articles = grouped.get(country, [])

        msg_id = send_message(f"📡 {country} 요약 시작...")

        result = f"📊 {country} 브리핑\n\n"

        for i, a in enumerate(articles):

            result += f"""
📰 {a['title']}

{summarize(a['title'] + a['summary'])}

🔗 {a['link']}
------------------
"""

        send_message(result)

        send_message("➡ 다시 실행하려면 GitHub Actions 재실행")


# =========================
if __name__ == "__main__":
    main()