from collector import collect_news
from summarizer import summarize
from telegram_sender import send_message
from dedup import is_duplicate, save_article

def main():

    news = collect_news()

    final_message = "📡 해외 방산 브리핑\n\n"

    article_count = 0

    for article in news:

        # 이미 보낸 기사면 건너뜀
        if is_duplicate(article["link"]):
            continue

        try:
            summarized = summarize(
                article["title"] + "\n" + article["summary"]
            )

            final_message += f"""
📰 {article['title']}

{summarized}

원문:
{article['link']}

------------------------
"""

            # 기사 저장
            save_article(article["link"])

            article_count += 1

        except Exception as e:
            print(f"요약 실패: {e}")

    # 새 기사 없을 경우
    if article_count == 0:
        final_message += "오늘 신규 방산 뉴스가 없습니다."

    # 텔레그램 전송
    send_message(final_message)

if __name__ == "__main__":
    main()