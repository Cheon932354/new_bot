import os
from collector import collect_news
from summarizer import summarize
from telegram_sender import send_message

def debug_env():
    print("\n========== ENV CHECK ==========")

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("OPENROUTER_API_KEY:",
          "OK" if openrouter_key else "MISSING")

    print("TELEGRAM_TOKEN:",
          "OK" if telegram_token else "MISSING")

    print("TELEGRAM_CHAT_ID:",
          chat_id if chat_id else "MISSING")

    print("================================\n")

def main():

    # 1. 환경변수 체크
    debug_env()

    # 2. 뉴스 수집 테스트
    print("[STEP 1] Collecting news...")
    news = collect_news()

    print(f"Collected articles: {len(news)}")

    if not news:
        print("❌ 뉴스 수집 실패")
        return

    # 3. AI 요약 테스트 (1개만 먼저)
    print("\n[STEP 2] Testing OpenRouter API...")

    test_article = news[0]["title"] + "\n" + news[0]["summary"]

    try:
        summary = summarize(test_article)
        print("✅ AI Summary 성공:\n")
        print(summary)

    except Exception as e:
        print("❌ AI API 실패:")
        print(str(e))
        return

    # 4. Telegram 테스트
    print("\n[STEP 3] Sending Telegram message...")

    try:
        send_message("🧪 테스트 메시지: API 정상 동작 확인")
        print("✅ Telegram 성공")

    except Exception as e:
        print("❌ Telegram 실패:")
        print(str(e))
        return

    # 5. 전체 브리핑 테스트
    print("\n[STEP 4] Full briefing test...")

    final_message = "📡 방산 브리핑 테스트\n\n"

    for article in news[:3]:

        try:
            summarized = summarize(
                article["title"] + "\n" + article["summary"]
            )

            final_message += f"""
📰 {article['title']}

{summarized}

🔗 {article['link']}
--------------------
"""

        except Exception as e:
            print("요약 실패:", article["title"])
            print(str(e))

    send_message(final_message)

    print("\n🎉 전체 프로세스 완료")

if __name__ == "__main__":
    main()