from collector import collect_news
from summarizer import summarize
from telegram import Bot
from telegram.ext import Updater, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os

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
    "인도": "🇮🇳"
}

def group_news_by_country(news):

    grouped = {}

    for article in news:

        country = article["country"]

        grouped.setdefault(country, []).append(article)

    return grouped

def create_buttons(news_by_country):

    keyboard = []

    for country, articles in news_by_country.items():

        flag = COUNTRIES.get(country, "🌐")

        keyboard.append([
            InlineKeyboardButton(
                f"{flag} {country} ({len(articles)})",
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

def button_callback(update, context):

    query = update.callback_query
    query.answer()

    country = query.data

    if country == "close":

        query.edit_message_text(
            "브리핑을 종료합니다."
        )

        return

    articles = news_cache.get(country, [])

    message = f"📡 {country} 방산 뉴스\n\n"

    for article in articles[:5]:

        summarized = summarize(
            article["title"] + "\n" + article["summary"]
        )

        short_summary = summarized[:120]

        message += f"""
📰 {article['title']}

→ {short_summary}

🔗 {article['link']}

----------------
"""

    query.edit_message_text(message)

def main():

    global news_cache

    news = collect_news()

    news_cache = group_news_by_country(news)

    keyboard = create_buttons(news_cache)

    summary_message = "📡 해외 방산 브리핑\n\n"

    summary_message += (
        "🌏 아시아 / 🌎 중남미 뉴스 현황\n\n"
    )

    total_articles = 0

    for country, articles in news_cache.items():

        flag = COUNTRIES.get(country, "🌐")

        summary_message += (
            f"{flag} {country} : {len(articles)}건\n"
        )

        total_articles += len(articles)

    summary_message += (
        f"\n📰 최근 7일 수집 기사 수: {total_articles}건"
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