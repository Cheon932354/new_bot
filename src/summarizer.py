from openai import OpenAI
import os
import re

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# HTML 제거
def clean_html(text):

    clean = re.compile('<.*?>')

    return re.sub(clean, '', text)

def summarize(title, summary):

    try:

        # HTML 제거
        summary = clean_html(summary)

        # 너무 긴 내용 자르기
        summary = summary[:500]

        prompt = f"""
다음 해외 방산뉴스를 한국어 브리핑 형식으로 정리해줘.

반드시 아래 형식으로 출력:

[한글 기사 제목]
(영문 기사 제목)

기사 내용 2줄 요약

조건:
- 자연스러운 한국어
- 핵심만
- 너무 길지 않게

기사 제목:
{title}

기사 내용:
{summary}
"""

        response = client.chat.completions.create(

            model="google/gemma-2-9b-it:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=150
        )

        # 응답 안정성 체크
        if (
            not response.choices
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):

            return f"""
{title}

요약 결과 없음
"""

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
        print(str(e))

        return f"""
{title}

기사 요약 실패
"""