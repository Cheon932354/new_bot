import os
from collector import collect_news
from summarizer import summarize
from telegram_sender import send_message


def debug_env():
    print("\n========== ENV CHECK ==========")

    print("OPENROUTER_API_KEY:",
          "OK" if os.getenv("OPENROUTER_API_KEY") else "MISSING")

    print("TELEGRAM_TOKEN:",
          "OK" if os.getenv("TELEGRAM_TOKEN") else "MISSING")

    print("TELEGRAM_CHAT_ID:",
          os.getenv("TELEGRAM_CHAT_ID") or "MISSING")

    print("================================\n")


def main():

    # 1. 환경 확인
    debug_env()

    # 2. 뉴스 수집
    print("[STEP 1] Collecting news...")
    news = collect_news()

    if not news:
        print("❌ 뉴스 수집 실패")
        return

    print(f"Collected: {len(news)} articles")

    # 3. OpenRouter 테스트 (1개만)
    print("\n[STEP 2] Testing AI summarizer...")

    try:
        test_text = news[0]["title"] + "\n" + news[0]["summary"]

        result = summarize(test_text)

        print("✅ AI 결과:\n")
        print(result)

    except Exception as e:
        print("❌ AI 오류:", str(e))
        return

    # 4. Telegram 테스트
    print("\n[STEP 3] Telegram test...")

    try:
        send_message("🧪 테스트 성공: 봇 정상 작동")
        print("✅ Telegram OK")

    except Exception as e:
        print("❌ Telegram 오류:", str(e))
        return

    # 5. 전체 브리핑 생성
    print("\n[STEP 4] Full briefing...")

    final_message = "📡 해외 방산 브리핑\n\n"

    for article in news[:3]:

        text = article["title"] + "\n" + article["summary"]

        try:
            summary = summarize(text)

            final_message += f"""
📰 {article['title']}

{summary}

🔗 {article['link']}
-----------------------
"""

        except Exception as e:
            print("요약 실패:", article["title"], e)

    send_message(final_message)

    print("\n🎉 완료")


if __name__ == "__main__":
    main()