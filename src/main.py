import os
import json
import time
import requests

from collector import collect_news
from summarizer import summarize


# =========================
# ENV
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# 상태 관리 (핵심)
# =========================
processed_update_ids = set()
processing = False


# =========================
# 국가 고정 리스트 (핵심)
# =========================
COUNTRIES = [
    "🇯🇵 일본",
    "🇵🇭 필리핀",
    "🇮🇩 인도네시아",
    "🇲🇾 말레이시아",
    "🇻🇳 베트남",
    "🇹🇭 태국",
    "🇧🇩 방글라데시",

    "🇵🇪 페루",
    "🇨🇱 칠레",
    "🇨🇴 콜롬비아",
    "🇦🇷 아르헨티나",
    "🇲🇽 멕시코",
    "🇧🇷 브라질",

    "🌍 기타 국가"
]


# =========================
# Telegram
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

    requests.post(
        BASE + "/editMessageText",
        json={
            "chat_id": CHAT_ID,
            "message_id": message_id,
            "text": text
        }
    )


# =========================
# 국가 감지 (기존 + fallback)
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

    return "🌍 기타 국가"


# =========================
# 뉴스 그룹핑
# =========================
def group_news(news_list):

    grouped = {}

    for n in news_list:

        title = n.get("title") or ""
        summary = n.get("summary") or ""

        country = detect_country(title + summary)

        grouped.setdefault(country, []).append(n)

    return grouped


# =========================
# UI (고정 국가 버튼)
# =========================
def build_keyboard(grouped):

    keyboard = []

    for c in COUNTRIES:

        count = len(grouped.get(c, []))

        keyboard.append([{
            "text": f"{c} ({count})",
            "callback_data": f"RUN|{c}"
        }])

    keyboard.append([{
        "text": "❌ 종료",
        "callback_data": "EXIT"
    }])

    return json.dumps({"inline_keyboard": keyboard})


# =========================
# 브리핑 실행 (중복 방지 핵심)
# =========================
def run_country(country, articles):

    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    time.sleep(0.5)

    edit_message(msg_id, f"📥 기사 {len(articles)}개 분석 시작")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    valid_count = 0

    for i, a in enumerate(articles):

        title = a.get("title", "")
        summary_raw = a.get("summary", "")
        link = a.get("link", "")

        if not title or not summary_raw:
            continue

        edit_message(msg_id, f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}")

        try:
            summary = summarize(title + " " + summary_raw)
        except:
            summary = "❌ 요약 실패"

        if not summary:
            summary = "요약 결과 없음"

        result += f"""
📰 {title}

{summary}

🔗 {link}
-----------------------
"""

        valid_count += 1
        time.sleep(0.8)

    edit_message(msg_id, "✅ 요약 완료!")

    if valid_count == 0:
        result += "\n⚠️ 표시할 뉴스가 없습니다."

    send_message(result)


# =========================
# callback 처리 (중복 방지 핵심)
# =========================
def handle_callback(data, news, grouped):

    global processing

    if processing:
        return

    processing = True

    try:

        if data == "EXIT":
            send_message("❌ 종료되었습니다.")
            return

        if data.startswith("RUN|"):

            country = data.split("|")[1].strip()

            articles = grouped.get(country, [])

            # 🔥 fallback (기타 포함 100% 보장)
            if not articles:

                send_message(f"⚠️ {country} 데이터 부족 → 전체 뉴스 사용")

                articles = [
                    n for n in news[:10]
                    if n.get("title") and n.get("summary")
                ]

            run_country(country, articles)

    finally:
        processing = False


# =========================
# polling (중복 방지)
# =========================
def listen_callbacks(news, grouped):

    last_update_id = None

    while True:

        try:
            res = requests.get(f"{BASE}/getUpdates").json()

            for update in res.get("result", []):

                uid = update["update_id"]

                # 🔥 중복 방지 핵심
                if uid in processed_update_ids:
                    continue

                processed_update_ids.add(uid)
                last_update_id = uid

                if "callback_query" in update:

                    data = update["callback_query"]["data"]

                    handle_callback(data, news, grouped)

        except Exception as e:
            print("polling error:", e)

        time.sleep(1)


# =========================
# MAIN
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

    listen_callbacks(news, grouped)


# =========================
if __name__ == "__main__":
    main()