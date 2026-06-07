# =========================
# src/summarizer.py
# OpenRouter 버전
# =========================

import os
from openai import OpenAI


# =========================
# CLIENT
# =========================
def get_client():

    api_key = os.getenv("OPENROUTER_API_KEY")

    print(
        "OPENROUTER KEY EXISTS:",
        bool(api_key)
    )

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


# =========================
# 제목 번역
# =========================
def translate_title(title):

    if not title:
        return ""

    try:

        client = get_client()

        response = client.chat.completions.create(

            model="google/gemini-2.5-flash",

            messages=[
                {
                    "role": "system",
                    "content":
                    "Translate defense news titles into natural Korean. Output Korean only."
                },
                {
                    "role": "user",
                    "content": title
                }
            ],

            max_tokens=100
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    except Exception as e:

        print("제목 번역 실패:", e)

        return title


# =========================
# 1줄 요약
# =========================
def summarize(text):

    if not text:

        return "기사 요약 정보 없음"

    try:

        client = get_client()

        response = client.chat.completions.create(

            model="google/gemini-2.5-flash",

            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    Summarize defense news in Korean.

                    Rules:
                    - One sentence only
                    - Maximum 50 characters
                    - Focus on the main defense event
                    """
                },
                {
                    "role": "user",
                    "content": text[:4000]
                }
            ],

            max_tokens=80
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    except Exception as e:

        print("요약 실패:", e)

        return "기사 핵심 내용 확인 필요"