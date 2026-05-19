from collector import collect_news
from summarizer import summarize
from telegram_sender import send_message

def main():

    news = collect_news()

    final_message = "📡 해외 방산 브리핑\n\n"

    for article in news[:5]:

        summarized = summarize(article["title"] + "\n" + article["summary"])

        final_message += f"""
📰 {article['title']}

{summarized}

원문:
{article['link']}

------------------------
"""

    send_message(final_message)

if __name__ == "__main__":
    main()