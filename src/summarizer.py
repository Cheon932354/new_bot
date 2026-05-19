from openai import OpenAI
import os
import re

# =========================
# API KEY 확인
# =========================

API_KEY = os.getenv("OPENROUTER_API_KEY")

print("========== DEBUG ==========")

if API_KEY:
    print("✅ OPENROUTER_API_KEY 로딩 성공")
    print(f"KEY 앞부분: {API_KEY[:15]}...")
else:
    print("❌ OPENROUTER_API_KEY 없음")

print("===========================")

# =========================
# OpenAI Client 생성
# =========================

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# =========================
# HTML 제거
# =========================

def clean_html(text):

    clean = re.compile('<.*?>')

    return re.sub(clean, '', text)

# =========================
# 기사 요약
# =========================

def summarize(title, summary):

    print("\n===========================")
    print("📰 기사 요약 시작")
    print(f"TITLE: {title}")
    print("===========================\n")

    try:

        summary = clean_html(summary)

        summary = summary[:300]

        prompt = f"""
다음 해외 방산뉴스를 한국어로 2줄 요약해줘.

반드시 한국어만 사용해라.

기사 제목:
{title}

기사 내용:
{summary}
"""

        print("📡 OpenRouter API 호출 시작")

        response = client.chat.completions.create(

            model="meta-llama/llama-3-8b-instruct:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=100
        )

        print("✅ OpenRouter API 호출 성공")

        # 응답 체크
        if (
            not response.choices
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):

            print("❌ 응답 데이터 없음")

            return f"""
📰 {title}

요약 결과 없음
"""

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print("✅ 요약 생성 성공")
        print("요약 결과:")
        print(result)

        return f"""
📰 {title}

{result}
"""

    except Exception as e:

        print("\n❌❌❌ API 오류 발생 ❌❌❌")
        print(type(e))
        print(str(e))
        print("❌❌❌❌❌❌❌❌❌❌\n")

        return f"""
📰 {title}

기사 요약 실패
"""