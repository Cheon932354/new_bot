
# =========================
# src/summarizer.py
# v2 최종 추천 버전
# =========================

import os
from openai import OpenAI


# =========================
# CLIENT
# =========================
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=API_KEY
)


# =========================
# 제목 번역
# =========================
def translate_title(title):

    if not title:
        return ""

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    """
                    당신은 방산 전문 번역가다.

                    규칙:
                    - 자연스러운 한국어
                    - 제목만 출력
                    - 설명 금지
                    """
                },

                {
                    "role": "user",
                    "content": title
                }
            ],

            max_tokens=120
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return result

    except Exception as e:

        print(
            "제목 번역 실패:",
            e
        )

        return title


# =========================
# 1줄 요약
# =========================
def summarize(title, summary):

    text = f"""
제목:
{title}

내용:
{summary}
"""

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    """
                    당신은 국방 전문 분석가다.

                    반드시 한국어로 작성하라.

                    규칙:

                    - 1문장만 작성
                    - 50자 이내
                    - 기사 핵심만 작성
                    - 불필요한 수식어 금지
                    - 문장 앞에 기호 금지
                    """
                },

                {
                    "role": "user",
                    "content": text
                }
            ],

            max_tokens=80
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return result

    except Exception as e:

        print(
            "요약 실패:",
            e
        )

        return (
            "기사 핵심 내용 확인 필요"
        )