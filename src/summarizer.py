from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# =========================
# 제목 번역
# =========================
def translate_title(title):

    try:

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
당신은 방산 전문 번역가이다.

규칙:
- 반드시 자연스러운 한국어로 번역
- 무기체계 명칭(F-35, Patriot, K9 등)은 유지
- 언론 기사 스타일로 번역
- 불필요한 설명 금지
"""
                },
                {
                    "role": "user",
                    "content": title
                }
            ],
            max_tokens=120
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("TITLE TRANSLATE ERROR:", e)
        return "번역 실패"


# =========================
# 3줄 요약
# =========================
def summarize(text):

    try:

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
당신은 한국 방산 전문 브리핑 분석관이다.

반드시 한국어로만 답변하라.

규칙:
- 영어 문장을 그대로 사용하지 말 것
- 무기체계 명칭(F-35, Patriot, K9 등)만 영어 유지 가능
- 나머지는 자연스러운 한국어로 번역
- 제목 반복 금지
- 반드시 정확히 3줄로 요약
- 각 줄은 반드시 "-" 로 시작
- 각 줄은 최대 40자 내외로 짧게 작성
- 문장은 반드시 완결형으로 끝낼 것
- 문장이 중간에 끊기지 않게 할 것
- 간결하고 전문적인 문체 사용
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "요약 실패"