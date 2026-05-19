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

# =========================
# 제목 번역
# =========================

def translate_title(title):

    try:

        prompt = f"""
다음 해외 방산뉴스 제목을
반드시 자연스러운 한국어 제목으로 번역해라.

영어를 그대로 출력하지 마라.

뉴스 제목:
{title}
"""

        response = client.chat.completions.create(

            model="meta-llama/llama-3-8b-instruct:free",

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

        return result

    except Exception as e:

        print("제목 번역 오류:")
        print(str(e))

        return title

# =========================
# 기사 요약
# =========================

def summarize(title, summary):

    try:

        summary = clean_html(summary)

        summary = summary[:300]

        # 제목 먼저 번역
        korean_title = translate_title(title)

        prompt = f"""
다음 해외 방산뉴스를
한국어로 2줄만 요약해줘.

반드시 한국어만 사용해라.

기사 제목:
{title}

기사 내용:
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

            max_tokens=120
        )

        summary_result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        final_result = f"""
{korean_title}
({title})

{summary_result}
"""

        return final_result

    except Exception as e:

        print("요약 오류:")
        print(str(e))

        return f"""
{title}

기사 요약 실패
"""