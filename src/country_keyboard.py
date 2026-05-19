import json

def build_country_keyboard(grouped):

    # 순서 고정 (중요)
    order = [
        # ASIA
        "🇵🇭 필리핀",
        "🇯🇵 일본",
        "🇮🇩 인도네시아",
        "🇲🇾 말레이시아",
        "🇻🇳 베트남",
        "🇹🇭 태국",
        "🇧🇩 방글라데시",
        "🌏 기타 아시아국가",

        # LATAM
        "🇵🇪 페루",
        "🇨🇱 칠레",
        "🇨🇴 콜롬비아",
        "🇦🇷 아르헨티나",
        "🇲🇽 멕시코",
        "🇧🇷 브라질",
        "🌎 기타 중남미",
    ]

    keyboard = []

    # 버튼 생성
    for country in order:

        count = len(grouped.get(country, []))

        if count > 0:
            keyboard.append([{
                "text": f"{country} ({count})",
                "callback_data": country
            }])

    # 종료 버튼
    keyboard.append([
        {"text": "❌ 종료", "callback_data": "exit"}
    ])

    return json.dumps({"inline_keyboard": keyboard})