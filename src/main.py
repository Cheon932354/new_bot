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

    data = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": text
    }

    requests.post(BASE + "/editMessageText", json=data)


# =========================
# AI 국가 분류
# =========================
def ai_detect_country(text):

    if not OPENROUTER_API_KEY:
        return "🌍 기타 국가"

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Return ONLY a country name like Japan, Brazil, India, Philippines. If unclear return Other."
                    },
                    {
                        "role": "user",
                        "content": text[:1000]
                    }
                ],
                "temperature": 0.2
            },
            timeout=10
        )

        result = res.json()["choices"][0]["message"]["content"].strip()

        return normalize_country(result)

    except:
        return "🌍 기타 국가"


# =========================
# 국가 정규화
# =========================
def normalize_country(name):

    name = name.lower()

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

    return mapping.get(name, "🌍 기타 국가")


# =========================
# 하이브리드 국가 감지
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

    return ai_detect_country(text)


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
# UI 키보드
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
# 브리핑 실행
# =========================
def run_country(country, articles):

    msg_id = send_message(f"📡 {country} 뉴스 수집 중...")

    time.sleep(0.5)

    edit_message(msg_id, f"📥 기사 {len(articles)}개 분석 완료")

    result = f"📊 <b>{country} 방산 브리핑</b>\n\n"

    for i, a in enumerate(articles):

        edit_message(msg_id, f"⏳ 요약 진행 중...\n{i+1}/{len(articles)}")

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
# callback 처리 (핵심)
# =========================
def handle_callback(data):

    if data == "EXIT":
        send_message("❌ 종료되었습니다.")
        return

    if data.startswith("RUN|"):

        country = data.split("|")[1].strip()

        news = collect_news()
        grouped = group_news(news)

        articles = grouped.get(country, [])

        # 🔥 기타 국가 fallback
        if len(articles) == 0:
            send_message(f"⚠️ {country} 데이터 부족 → 전체 뉴스 일부 표시")
            articles = news[:5]

        run_country(country, articles)


# =========================
# polling (옵션 B 핵심)
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

    listen_callbacks()


# =========================
if __name__ == "__main__":
    main()