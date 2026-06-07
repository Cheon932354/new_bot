# =========================
# src/main.py
# PART 1
# =========================

import os
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

import holidays

from collector import collect_news
from summarizer import (
    summarize,
    translate_title
)


# =========================
# TELEGRAM
# =========================
TOKEN = os.getenv(
    "TELEGRAM_TOKEN"
)

CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

BASE = (
    f"https://api.telegram.org/bot{TOKEN}"
)


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

    return datetime.now(

        ZoneInfo(
            "Asia/Seoul"
        )

    ).strftime("%Y-%m-%d")


# =========================
# WORKDAY CHECK
# =========================
def is_workday():

    now = datetime.now(

        ZoneInfo(
            "Asia/Seoul"
        )
    )

    today = now.date()

    if now.weekday() >= 5:

        print(
            "주말 - 미실행"
        )

        return False

    kr_holidays = holidays.KR()

    if today in kr_holidays:

        print(
            "공휴일 - 미실행"
        )

        return False

    return True


# =========================
# COUNTRY DETECT
# =========================
def detect_country(text):

    t = (
        text or ""
    ).lower()

    mapping = {

        # 아시아
        "japan":"🇯🇵 일본",
        "india":"🇮🇳 인도",
        "philippines":"🇵🇭 필리핀",
        "indonesia":"🇮🇩 인도네시아",
        "malaysia":"🇲🇾 말레이시아",
        "vietnam":"🇻🇳 베트남",
        "thailand":"🇹🇭 태국",
        "bangladesh":"🇧🇩 방글라데시",
        "cambodia":"🇰🇭 캄보디아",

        # 중앙아시아
        "uzbekistan":"🇺🇿 우즈베키스탄",
        "kazakhstan":"🇰🇿 카자흐스탄",
        "kyrgyzstan":"🇰🇬 키르기스스탄",

        # 중남미
        "brazil":"🇧🇷 브라질",
        "chile":"🇨🇱 칠레",
        "peru":"🇵🇪 페루",
        "colombia":"🇨🇴 콜롬비아",
        "argentina":"🇦🇷 아르헨티나",
        "uruguay":"🇺🇾 우루과이",
        "ecuador":"🇪🇨 에콰도르",
        "mexico":"🇲🇽 멕시코"
    }

    for k, v in mapping.items():

        if k in t:

            return v

    return None


# =========================
# 국내 방산 기사
# =========================
def is_korean_defense_news(article):

    source = article.get(
        "source",
        ""
    )

    korean_sources = [

        "연합뉴스 정치",
        "국방일보",
        "디펜스타임즈"
    ]

    if source not in korean_sources:

        return False

    text = (

        article.get(
            "title",
            ""
        )

        + " "

        + article.get(
            "summary",
            ""
        )

    ).lower()

    keywords = [

        "한화",
        "현대로템",
        "lig",
        "대한항공",

        "k2",
        "k9",
        "kf-21",
        "천무",
        "redback",

        "방산",
        "국방",
        "수출",
        "협력",
        "미사일",
        "전차",
        "장갑차",
        "전투기",
        "잠수함",

        "브라질",
        "인도",
        "필리핀",
        "인도네시아",
        "말레이시아",
        "태국",
        "베트남",
        "칠레",
        "페루",
        "콜롬비아",
        "아르헨티나",
        "우루과이",
        "에콰도르",
        "멕시코"
    ]

    return any(
        k.lower() in text
        for k in keywords
    )


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
        "🇰🇭 캄보디아": [],

        "🇨🇱 칠레": [],
        "🇵🇪 페루": [],
        "🇨🇴 콜롬비아": [],
        "🇦🇷 아르헨티나": [],
        "🇺🇾 우루과이": [],
        "🇪🇨 에콰도르": [],
        "🇲🇽 멕시코": [],

        "🇰🇷 국내 기타": []
    }

    foreign = {

        "🇯🇵 일본": [],
        "🇮🇳 인도": [],
        "🇵🇭 필리핀": [],
        "🇮🇩 인도네시아": [],
        "🇲🇾 말레이시아": [],
        "🇻🇳 베트남": [],
        "🇹🇭 태국": [],
        "🇧🇩 방글라데시": [],
        "🇰🇭 캄보디아": [],

        "🇺🇿 우즈베키스탄": [],
        "🇰🇿 카자흐스탄": [],
        "🇰🇬 키르기스스탄": [],

        "🇧🇷 브라질": [],
        "🇨🇱 칠레": [],
        "🇵🇪 페루": [],
        "🇨🇴 콜롬비아": [],
        "🇦🇷 아르헨티나": [],
        "🇺🇾 우루과이": [],
        "🇪🇨 에콰도르": [],
        "🇲🇽 멕시코": []
    }

    for n in news:

        combined = (
            n.get("title", "")
            + " "
            + n.get("summary", "")
        )

        if is_korean_defense_news(n):

            country = detect_country(
                combined
            )

            if (
                country
                and country in domestic
            ):
                domestic[country].append(
                    n
                )
            else:
                domestic[
                    "🇰🇷 국내 기타"
                ].append(n)

            continue

        country = detect_country(
            combined
        )

        if (
            country
            and country in foreign
        ):
            foreign[country].append(
                n
            )

    return domestic, foreign

# =========================
# COUNT MESSAGE
# =========================
def build_count_message(
    domestic,
    foreign
):

    date = get_date()

    msg = (
        f"📊 <b>일일 방산 브리핑 "
        f"({date})</b>\n\n"
    )

    msg += (
        "━━━━━━━━━━━━━━━\n"
        "🇰🇷 <b>국내 방산 뉴스</b>\n"
        "━━━━━━━━━━━━━━━\n"
    )

    for country, articles in domestic.items():

        msg += (
            f"{country} : "
            f"{len(articles)}건\n"
        )

    msg += "\n"

    msg += (
        "━━━━━━━━━━━━━━━\n"
        "🌏 <b>해외 방산 뉴스</b>\n"
        "━━━━━━━━━━━━━━━\n"
    )

    for country, articles in foreign.items():

        msg += (
            f"{country} : "
            f"{len(articles)}건\n"
        )

    return msg


# =========================
# BUILD MESSAGE
# =========================
def build_message(
    title_text,
    articles
):

    msg = (
        "━━━━━━━━━━━━━━━\n"
        f"{title_text}\n\n"
    )

    for a in articles:

        title = a.get(
            "title",
            ""
        )

        summary_raw = a.get(
            "summary",
            ""
        )

        link = a.get(
            "link",
            ""
        )

        published = (
            a.get(
                "published",
                ""
            )
            or ""
        )

        translated_title = (
            translate_title(
                title
            )
        )

        summary = summarize(
            title,
            summary_raw
        )

        if published:

            published = (
                str(published)[:16]
            )

        else:

            published = (
                "날짜 정보 없음"
            )

        msg += f"""
📰 <b>원문 제목</b>
{title}

🇰🇷 <b>한글 제목</b>
{translated_title}

📅 <b>발행일</b>
{published}

📌 <b>핵심</b>
{summary}

🔗 <a href="{link}">기사 보기</a>

────────────────

"""

    return msg


# =========================
# MAIN
# =========================
def main():

#    if not is_workday():

#        print(
#            "주말/공휴일 종료"
#        )

 #       return

    if False:
        return

    print(
        "🚀 뉴스 수집 시작"
    )

    news = collect_news()

    print(
        f"수집 기사 수: "
        f"{len(news)}"
    )

    domestic, foreign = (
        group_news(news)
    )

    domestic_msgs = []
    foreign_msgs = []

    # =====================
    # 국내 브리핑 생성
    # =====================
    for country, articles in domestic.items():

        if not articles:
            continue

        print(
            f"국내 {country} "
            f"요약 생성"
        )

        domestic_msgs.append(

            build_message(

                f"🇰🇷 <b>국내 방산 뉴스"
                f" - {country}</b>",

                articles
            )
        )

    # =====================
    # 해외 브리핑 생성
    # =====================
    for country, articles in foreign.items():

        if not articles:
            continue

        print(
            f"해외 {country} "
            f"요약 생성"
        )

        foreign_msgs.append(

            build_message(

                f"🌏 <b>해외 방산 뉴스"
                f" - {country}</b>",

                articles
            )
        )

    print(
        "✅ 모든 기사 요약 완료"
    )

    # =====================
    # 브리핑 시작
    # =====================
    send_message(

        build_count_message(
            domestic,
            foreign
        )
    )

    # =====================
    # 국내
    # =====================
    for msg in domestic_msgs:

        send_message(msg)

    # =====================
    # 해외
    # =====================
    for msg in foreign_msgs:

        send_message(msg)

    # =====================
    # 종료
    # =====================
    send_message(

        "✅ <b>일일 방산 브리핑 종료</b>"
    )

    print(
        "✅ 전체 완료"
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":

    main()