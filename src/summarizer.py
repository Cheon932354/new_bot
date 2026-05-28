from openai import OpenAI
import os


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# =========================
# 제목 번역
# =========================
def translate_title(title):

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content":
                    "Translate defense news titles into natural Korean."
                },
                {
                    "role": "user",
                    "content": title
                }
            ],

            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("제목 번역 실패:", e)

        return title


# =========================
# 뉴스 요약
# =========================
def summarize(text):

    # =========================
    # fallback
    # =========================
    if not text or len(text.strip()) < 80:

        return (
            "• 기사 본문 요약 데이터 부족\n"
            "• RSS 원문 기반 최신 방산 기사\n"
            "• 상세 내용은 원문 기사 참고"
        )

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    """
                    You are a defense news analyst.

                    Summarize into Korean.

                    Rules:
                    - EXACTLY 3 bullet points
                    - concise but informative
                    - preserve military/defense meaning
                    - each bullet under 2 lines
                    - no markdown
                    """
                },

                {
                    "role": "user",
                    "content": text
                }
            ],

            max_tokens=220
        )

        result = response.choices[0].message.content.strip()

        # 빈 응답 방지
        if not result:

            return (
                "• 요약 생성 실패\n"
                "• 원문 기사 참고 필요\n"
                "• 링크 통해 상세 확인 가능"
            )

        return result

    except Exception as e:

        print("요약 실패:", e)

        return (
            "• OpenAI 요약 실패\n"
            "• API 제한 또는 RSS 문제 가능\n"
            "• 원문 기사 참고"
        )