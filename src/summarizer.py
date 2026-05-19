from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def summarize(article):

    prompt = f"""
다음 해외 방산 뉴스를:

1. 한국어로 번역
2. 3줄로 요약
3. 중요도를 1~5로 평가
4. 관련 국가/군종/기업 태그 생성

형식:

[제목]
[요약]
[중요도]
[태그]

기사:
{article}
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
