from telegram import Bot
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)