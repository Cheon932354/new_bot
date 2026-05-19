from collector import collect_news
from summarizer import summarize
from telegram import Bot
from telegram.ext import Updater, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

news_cache = {}

COUNTRIES = {
    "브라질": "🇧🇷",
    "칠레": "🇨🇱",
    "페루": "🇵🇪",
    "에콰도르": "🇪🇨",
    "콜롬비아": "🇨🇴",
    "아르헨티나": "🇦🇷",
    "베트남": "🇻🇳",
    "태국": "🇹🇭",
    "필리핀": "🇵🇭",
    "인도네시아": "🇮🇩",
    "인도": "🇮🇳",
    "한국기업": "🇰🇷"
}

def group_news_by_country(news):

    grouped = {}

    for article in news:

        country = article["country"]

        grouped.setdefault(country, []).append(article)

    return grouped

# =========================
# 버튼 생성
# =========================

def create_country_buttons():

    keyboard = []

    for country in news_cache.keys():

        flag = COUNTRIES.get(country, "🌐")

        keyboard.append([
            InlineKeyboardButton(
                f"{flag} {country}",
                callback_data=country
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ 종료",
            callback_data="close"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

# =========================
# 버튼 클릭 처리
# =========================

def button_callback(update, context):

    query = update.callback_query
    query.answer()

    country = query.data

    # 종료 버튼
    if country == "close":

        query.edit_message_text(
            "❌ 브리핑 종료"
        )

        return

    articles = news_cache.get(country, [])

    # 뉴스 수집중 UI
    query.edit_message_text(
        f"📡 {country} 뉴스 수집중..."
    )

    time.sleep(1)

    # AI 요약중 UI
    query.edit_message_text(
        f"🤖 {country} AI 요약중..."
    )

    time.sleep(1)

    message = f"✅ {country} 방산뉴스 브리핑\n\n"

    # 기사 출력
    for article in articles[:5]:

        summarized = summarize(
            article["title"]
        )

        message += f"""
📰 {article['title']}

→ {summarized}

🔗 {article['link']}

----------------
"""

    # 다시 버튼 생성
    keyboard = create_country_buttons()

    # 기사 + 버튼 함께 출력
    query.edit_message_text(
        text=message,
        reply_markup=keyboard
    )

# =========================
# 메인
# =========================

def main():

    global news_cache

    news = collect_news()

    news_cache = group_news_by_country(news)

    keyboard = create_country_buttons()

    summary_message = (
        "📡 해외 방산 브리핑\n\n"
    )

    total_articles = 0

    for country, articles in news_cache.items():

        flag = COUNTRIES.get(country, "🌐")

        summary_message += (
            f"{flag} {country} ({len(articles)})\n"
        )

        total_articles += len(articles)

    summary_message += (
        f"\n📰 최근 7일 기사 수: {total_articles}건\n\n"
        "원하는 국가를 선택하세요."
    )

    bot.send_message(
        chat_id=CHAT_ID,
        text=summary_message,
        reply_markup=keyboard
    )

    updater = Updater(
        TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CallbackQueryHandler(button_callback)
    )

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()