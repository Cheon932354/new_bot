from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

def create_country_buttons(news_by_country):

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