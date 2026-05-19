from collector import collect_news
from summarizer import summarize
from telegram import Bot
from telegram.ext import Updater, CallbackQueryHandler
from ui_bot import create_country_buttons
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

news_cache = {}

def group_news_by_country(news):

    grouped = {}

    country_keywords = [
        "Brazil",
        "Chile",
        "Peru",
        "Ecuador",
        "Colombia",
        "Argentina",
        "Vietnam",
        "Thailand",
        "Philippines",
        "Indonesia",
        "India"
    ]

    kor_names = {
        "Brazil": "브라질",
        "Chile": "칠레",
        "Peru": "페루",
        "Ecuador": "에콰도르",
        "Colombia": "콜롬비아",
        "Argentina": "아르헨티나",
        "Vietnam": "베트남",
        "Thailand": "태국",
        "Philippines": "필리핀",
        "Indonesia": "인도네시아",
        "India": "인도"
    }

    for article in news:

        for keyword in country_keywords:

            if keyword.lower() in article["title"].lower():

                country = kor_names[keyword]

                grouped.setdefault(country, []).append(article)

    return grouped

def button_callback(update, context):

    query = update.callback_query
    query.answer()

    country = query.data

    if country == "close":

        query.edit_message_text("브리핑을 종료합니다.")
        return

    articles = news_cache.get(country, [])

    message = f"📡 {country} 방산 뉴스\n\n"

    for article in articles[:5]:

        summarized = summarize(article["title"])

        message += f"""
📰 {article['title']}
→ {summarized[:100]}

🔗 {article['link']}

----------------
"""

    query.edit_message_text(message)

def main():

    global news_cache

    news = collect_news()

    news_cache = group_news_by_country(news)

    keyboard = create_country_buttons(news_cache)

    summary_message = "📡 해외 방산 브리핑\n\n"

    summary_message += "🌏 아시아 / 🌎 중남미 뉴스 현황\n\n"

    for country, articles in news_cache.items():

        summary_message += f"{country}: {len(articles)}건\n"

    bot.send_message(
        chat_id=CHAT_ID,
        text=summary_message,
        reply_markup=keyboard
    )

    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CallbackQueryHandler(button_callback)
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()