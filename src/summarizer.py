# =========================
# src/summarizer.py
# =========================

import os
from openai import OpenAI


# =========================
# CLIENT
# =========================
def get_client():

    api_key = os.getenv("OPENAI_API_KEY")

    print("OPENAI EXISTS:", api_key is not None)

    return OpenAI(api_key=api_key)


# =========================
# 제목 번역
# =========================
def translate_title(title):

    try:

        client = get_client()

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

        result = response.choices[0].message.content.strip()

        return result

    except Exception as e:

        print("제목 번역 실패:", e)

        return title


# =========================
# 뉴스 요약
# =========================
def summarize(text):

    # fallback
    if not text or len(text.strip()) < 80:

        return (
            "• 기사 본문 요약 데이터 부족\n"
            "• RSS 기반 최신 방산 기사\n"
            "• 상세 내용은 원문 기사 참고"
        )

    try:

        client = get_client()

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    """
                    Summarize this defense news in Korean.

                    Rules:
                    - EXACTLY 3 bullet points
                    - concise
                    - preserve military meaning
                    - each bullet short
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

        return result

    except Exception as e:

        print("요약 실패:", e)

        return (
            "• OpenAI 요약 실패\n"
            "• API 또는 RSS 문제 가능\n"
            "• 원문 기사 참고"
        )