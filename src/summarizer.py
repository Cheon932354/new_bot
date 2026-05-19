from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def summarize(title, summary):

    try:

        content = f"""
제목:
{title}

내용:
{summary}
"""

        # 너무 긴 기사 자르기
        content = content[:2000]

        prompt = f"""
아래 해외 방산뉴스를 한국어 브리핑 형식으로 정리해줘.

반드시 아래 형식으로 출력:

[한글 기사 제목]
(영문 기사 제목)

기사 내용 2줄 요약

조건:
- 자연스러운 한국어
- 너무 길지 않게
- 핵심만 요약
- 2줄 이내

기사:
{content}
"""

        response = client.chat.completions.create(

            model="mistralai/mistral-7b-instruct:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=200
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

        print("요약 오류:")
        print(e)

        return f"""
{title}

기사 요약 실패
"""