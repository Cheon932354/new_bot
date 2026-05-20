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
                    "content": "Translate the defense news title into natural Korean."
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
Summarize the defense news in Korean within 3 concise bullet points.

IMPORTANT:
- Do NOT repeat the title
- Focus only on 핵심 내용
- Keep it short and professional
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=200
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "요약 실패"