from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def summarize(article):

    try:

        article = article[:1000]

        prompt = f"""
아래 방산뉴스 제목을 한국어 한줄로 짧게 요약해줘.

기사:
{article}
"""

        response = client.chat.completions.create(

            model="mistralai/mistral-7b-instruct:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=60
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        if len(result) < 3:
            return article[:80]

        return result

    except Exception as e:

        print("요약 오류:")
        print(e)

        return article[:80]