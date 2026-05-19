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

        # 너무 긴 내용 제거
        summary = summary[:300]

        prompt = f"""
당신은 한국 방산 전문 뉴스 브리퍼다.

반드시 모든 내용을 한국어로 번역해서 출력해라.

영어 문장을 그대로 출력하지 마라.

출력 형식:

[한글 기사 제목]
(원문 영문 제목)

한국어 기사 내용 2줄 요약

규칙:
- 반드시 한국어 사용
- 자연스럽게 번역
- 핵심만 간단히
- 2줄 이내 요약

원문 기사 제목:
{title}

원문 기사 내용:
{summary}
"""

        response = client.chat.completions.create(

            model="meta-llama/llama-3-8b-instruct:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=180
        )

        # 응답 체크
        if (
            not response.choices
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):

            return f"""
{title}

번역 결과 없음
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