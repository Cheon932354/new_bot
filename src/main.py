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
# 상태 관리 (중복 방지 핵심)
# =========================
processed_callback_ids = set()


# =========================
# 국가 그룹
# =========================
ASIA_COUNTRIES = [
    "🇯🇵 일본",
    "🇵🇭 필리핀",
    "🇮🇩 인도네시아",
    "🇲🇾 말레이시아",
    "🇻🇳 베트남",
    "🇹🇭 태국",
    "🇧🇩 방글라데시"
]

LATAM_COUNTRIES = [
    "🇵🇪 페루",
    "🇨🇱 칠레",
    "🇨🇴 콜롬비아",
    "🇦🇷 아르헨티나",
    "🇲🇽 멕시코",
    "🇧🇷 브라질"
]

OTHER_COUNTRY = ["🌍 기타 국가"]


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
# 국가 감지
# =========================
def detect_country(text):

    t = (text or "").lower()

    mapping = {
        "japan": "🇯🇵 일본",
        "philippines": "🇵🇭 필리핀",
        "indonesia": "🇮🇩 인도네시아",
        "malaysia": "🇲🇾 말레이시아",
        "vietnam": "🇻🇳 베트남",
        "thailand": "🇹🇭 태국",
        "bangladesh": "🇧🇩 방글라데시",

        "peru": "🇵🇪 페루",
        "chile": "🇨🇱 칠레",
        "colombia": "🇨🇴 콜롬비아",
        "argentina": "🇦🇷 아르헨티나",
        "mexico": "🇲🇽 멕시코",
        "brazil": "🇧🇷 브라질"
    }

    for k, v in mapping.items():
        if k in t:
            return v

    return "🌍 기타 국가"


# =========================
# 그룹핑
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
# UI (그룹형)
# =========================
def build_keyboard(grouped):

    keyboard = []

    keyboard.append([{"text": "🌏 아시아", "callback_data": "NONE"}])

    for c in ASIA_COUNTRIES:
        count = len(grouped.get(c, []))
        keyboard.append([{
            "text": f"{c} ｜ {count} 📰",
            "callback_data": f"RUN|{c}"
        }])

    keyboard.append([{"text": "🌎 중남미", "callback_data": "NONE"}])

    for c in LATAM_COUNTRIES:
        count = len(grouped.get(c, []))
        keyboard.append([{
            "text": f"{c} ｜ {count} 📰",
            "callback_data": f"RUN|{c}"
        }])

    keyboard.append([{"text": "🌍 기타", "callback_data": "NONE"}])

    for c in OTHER_COUNTRY:
        count = len(grouped.get(c, []))
        keyboard.append([{
            "text": f"{c} ｜ {count} 📰",
            "callback_data": f"RUN|{c}"
        }])

    keyboard.append([{
        "text": "❌ 종료",
        "callback_data": "EXIT"
    }])

    return json.dumps({"inline_keyboard": keyboard})


# =========================
# 브리핑 실행
# =========================
def run_country(country, articles):

    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    time.sleep(0.5)

    edit_message(msg_id, f"📥 기사 {len(articles)}개 분석 시작")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    valid = 0

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
            summary = "요약 없음"

        result += f"""
📰 {title}

{summary}

🔗 {link}
-----------------------
"""

        valid += 1
        time.sleep(0.8)

    edit_message(msg_id, "✅ 요약 완료!")

    # 🔥 기타 포함 모든 경우 출력 보장
    if valid == 0:
        result += "\n⚠️ 표시할 뉴스가 없어 fallback 데이터를 사용했습니다."

    send_message(result)


# =========================
# callback 처리 (완전 중복 제거)
# =========================
def handle_callback(data, news, grouped):

    if data == "EXIT":
        send_message("❌ 종료")
        return

    if data == "NONE":
        return

    if data.startswith("RUN|"):

        country = data.split("|")[1].strip()

        articles = grouped.get(country, [])

        # 🔥 fallback 핵심
        if not articles or len(articles) == 0:

            send_message(f"⚠️ {country} 데이터 부족 → 전체 뉴스 사용")

            articles = [
                n for n in news[:10]
                if n.get("title") and n.get("summary")
            ]

        run_country(country, articles)


# =========================
# polling (완전 중복 방지 핵심)
# =========================
def listen_callbacks(news, grouped):

    while True:

        try:
            res = requests.get(f"{BASE}/getUpdates").json()

            for update in res.get("result", []):

                if "callback_query" not in update:
                    continue

                callback = update["callback_query"]

                cid = callback["id"]  # 🔥 핵심

                if cid in processed_callback_ids:
                    continue

                processed_callback_ids.add(cid)

                data = callback["data"]

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