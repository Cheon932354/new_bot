import os
import requests
from datetime import datetime

from collector import collect_news
from summarizer import summarize, translate_title


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# SEND MESSAGE
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
# DATE
# =========================
def get_date():
    return datetime.now().strftime("%Y-%m-%d")


# =========================
# COUNTRY DETECT
# =========================
def detect_country(text):

    t = (text or "").lower()

    mapping = {

        # =========================
        # 아시아
        # =========================
        "japan":"🇯🇵 일본",
        "philippines":"🇵🇭 필리핀",
        "indonesia":"🇮🇩 인도네시아",
        "malaysia":"🇲🇾 말레이시아",
        "vietnam":"🇻🇳 베트남",
        "thailand":"🇹🇭 태국",
        "bangladesh":"🇧🇩 방글라데시",
        "india":"🇮🇳 인도",

        # =========================
        # 중앙아시아
        # =========================
        "uzbekistan":"🇺🇿 우즈베키스탄",
        "kazakhstan":"🇰🇿 카자흐스탄",
        "kyrgyzstan":"🇰🇬 키르기스스탄",

        # =========================
        # 중남미
        # =========================
        "peru":"🇵🇪 페루",
        "chile":"🇨🇱 칠레",
        "colombia":"🇨🇴 콜롬비아",
        "argentina":"🇦🇷 아르헨티나",
        "mexico":"🇲🇽 멕시코",
        "brazil":"🇧🇷 브라질",
    }

    for k, v in mapping.items():

        if k in t:
            return v

    return None


# =========================
# 국내 방산 기사 판단
# =========================
def is_korean_defense_news(article):

    source = article.get("source", "")

    korean_sources = [
        "연합뉴스 정치",
        "국방일보",
        "디펜스타임즈"
    ]

    if source not in korean_sources:
        return False

    text = (
        article.get("title", "")
        + " "
        + article.get("summary", "")
    ).lower()

    defense_keywords = [

        # 방산업체
        "hanwha",
        "hyundai rotem",
        "lig nex1",
        "대한항공",

        "한화",
        "현대로템",
        "lig넥스원",
        "대한항공",

        # 무기체계
        "kf-21",
        "k9",
        "k2",
        "천무",
        "redback",
        "장갑차",
        "전차",
        "미사일",
        "전투기",
        "잠수함",
        "호위함",

        # 방산 일반
        "방산",
        "국방",
        "무기",
        "수출",
        "협력",

        # 국가
        "브라질",
        "인도",
        "필리핀",
        "인도네시아",
        "페루",
        "칠레",
        "콜롬비아",
        "아르헨티나",
        "멕시코",
        "말레이시아",
        "태국",
        "베트남",
        "방글라데시",
    ]

    for keyword in defense_keywords:

        if keyword.lower() in text:
            return True

    return False


# =========================
# GROUP NEWS
# =========================
def group_news(news):

    domestic = {

        "🇧🇷 브라질": [],
        "🇮🇳 인도": [],
        "🇵🇭 필리핀": [],
        "🇮🇩 인도네시아": [],
        "🇲🇾 말레이시아": [],
        "🇻🇳 베트남": [],
        "🇹🇭 태국": [],
        "🇧🇩 방글라데시": [],

        "🇵🇪 페루": [],
        "🇨🇱 칠레": [],
        "🇨🇴 콜롬비아": [],
        "🇦🇷 아르헨티나": [],
        "🇲🇽 멕시코": [],

        "🇰🇷 기타 국내": []
    }

    foreign = {

        "🇯🇵 일본": [],
        "🇵🇭 필리핀": [],
        "🇮🇩 인도네시아": [],
        "🇲🇾 말레이시아": [],
        "🇻🇳 베트남": [],
        "🇹🇭 태국": [],
        "🇧🇩 방글라데시": [],
        "🇮🇳 인도": [],

        "🇺🇿 우즈베키스탄": [],
        "🇰🇿 카자흐스탄": [],
        "🇰🇬 키르기스스탄": [],

        "🇵🇪 페루": [],
        "🇨🇱 칠레": [],
        "🇨🇴 콜롬비아": [],
        "🇦🇷 아르헨티나": [],
        "🇲🇽 멕시코": [],
        "🇧🇷 브라질": [],

        # 신규 추가
        "🌍 기타 해외": [],
    }

    for n in news:

        title = n.get("title", "")
        summary = n.get("summary", "")

        combined = title + " " + summary

        # =========================
        # 국내 방산 뉴스
        # =========================
        if is_korean_defense_news(n):

            country = detect_country(combined)

            if country and country in domestic:
                domestic[country].append(n)
            else:
                domestic["🇰🇷 기타 국내"].append(n)

            continue

        # =========================
        # 해외 방산 뉴스
        # =========================
        country = detect_country(combined)

        # 국가 인식 실패 시 기타 해외
        if not country:

            foreign["🌍 기타 해외"].append(n)
            continue

        if country in foreign:
            foreign[country].append(n)

    return domestic, foreign


# =========================
# COUNT MESSAGE
# =========================
def build_count_message(domestic, foreign):

    date = get_date()

    msg = f"📊 <b>방산 뉴스 업데이트 ({date})</b>\n\n"

    # =========================
    # 국내
    # =========================
    msg += "━━━━━━━━━━━━━━━\n"
    msg += "🇰🇷 <b>국내 방산 뉴스</b>\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    for country, articles in domestic.items():

        msg += f"{country} : {len(articles)}건\n"

    msg += "\n"

    # =========================
    # 해외
    # =========================
    msg += "━━━━━━━━━━━━━━━\n"
    msg += "🌏 <b>해외 방산 뉴스</b>\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    for country, articles in foreign.items():

        msg += f"{country} : {len(articles)}건\n"

    return msg


# =========================
# BUILD MESSAGE
# =========================
def build_message(title_text, articles):

    msg = f"━━━━━━━━━━━━━━━\n"
    msg += f"{title_text}\n\n"

    for a in articles:

        title = a.get("title", "")
        summary_raw = a.get("summary", "")
        link = a.get("link", "")

        published = (
            a.get("published")
            or ""
        )

        if published:
            published = str(published)[:16]
            title_line = f"{title} ({published})"
        else:
            title_line = title

        translated_title = translate_title(title)

        summary = summarize(summary_raw)

        msg += f"""
📰 <b>원문 제목</b>
{title_line}

🇰🇷 <b>한글 제목</b>
{translated_title}

📌 <b>3줄 요약</b>
{summary}

🔗 <a href="{link}">기사 보기</a>

────────────────
"""

    return msg


# =========================
# MAIN
# =========================
def main():

    print("🚀 뉴스 수집 시작")

    news = collect_news()

    print(f"수집 기사 수: {len(news)}")

    domestic, foreign = group_news(news)

    domestic_msgs = []
    foreign_msgs = []

    # =========================
    # 국내 브리핑
    # =========================
    for country, articles in domestic.items():

        if not articles:
            continue

        print(f"국내 {country} 요약 중...")

        msg = build_message(
            f"🇰🇷 <b>국내 방산 뉴스 - {country}</b>",
            articles
        )

        domestic_msgs.append(msg)

    # =========================
    # 해외 브리핑
    # =========================
    for country, articles in foreign.items():

        if not articles:
            continue

        print(f"해외 {country} 요약 중...")

        msg = build_message(
            f"🌏 <b>해외 방산 뉴스 - {country}</b>",
            articles
        )

        foreign_msgs.append(msg)

    print("✅ 모든 뉴스 요약 완료")

    # =========================
    # 뉴스 현황
    # =========================
    send_message(
        build_count_message(
            domestic,
            foreign
        )
    )

    # =========================
    # 국내 브리핑
    # =========================
    for msg in domestic_msgs:
        send_message(msg)

    # =========================
    # 해외 브리핑
    # =========================
    for msg in foreign_msgs:
        send_message(msg)

    # =========================
    # 종료
    # =========================
    send_message(
        "✅ <b>일일 방산 브리핑 종료</b>"
    )

    print("✅ 전체 완료")


if __name__ == "__main__":
    main()