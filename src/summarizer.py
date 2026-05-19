import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def summarize(text):

    if not text:
        return "❌ 입력 없음"

    prompt = f"""
너는 방산 전문 분석가다.

다음 해외 방산 뉴스를 아래 형식으로 정리해라:

[출력 형식]
1. 한국어 번역
2. 3줄 요약
3. 중요도 (1~5)
4. 국가 / 군종 / 기업 태그

[기사]
{text}
"""

    try:
        response = client.chat.completions.create(
            # ✅ 현재 OpenRouter에서 안정적으로 동작하는 모델
            model="google/gemma-7b-it",

            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ OpenRouter API 오류: {str(e)}"