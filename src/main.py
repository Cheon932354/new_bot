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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# TELEGRAM
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
# 국가 감지 (AI + rule)
# =========================
def detect_country(text):

    t = text.lower()

    # 1차 rule
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

    # fallback
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
# 키보드
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
# 🔥 핵심: 안전한 브리핑 실행
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

        # 🔥 완전 방어
        if not title or not summary_raw:
            continue

        edit_message(msg_id, f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}")

        try:
            summary = summarize(title + " " + summary_raw)
        except Exception as e:
            summary = f"❌ 요약 실패"

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

    # 🔥 핵심: 기타 포함 모든 케이스 보장
    if valid_count == 0:
        result += "\n⚠️ 표시할 뉴스가 부족하여 기본 데이터를 출력합니다."

    send_message(result)


# =========================
# callback 처리
# =========================
def handle_callback(data, news, grouped):

    if data == "EXIT":
        send_message("❌ 종료되었습니다.")
        return

    if data.startswith("RUN|"):

        country = data.split("|")[1].strip()

        articles = grouped.get(country, [])

        # 🔥 기타 국가 100% 보장 fallback
        if not articles or len(articles) == 0:

            send_message(f"⚠️ {country} 데이터 부족 → 전체 뉴스 기반으로 재구성")

            articles = [
                n for n in news[:10]
                if n.get("title") and n.get("summary")
            ]

        run_country(country, articles)


# =========================
# polling
# =========================
def listen_callbacks(news, grouped):

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