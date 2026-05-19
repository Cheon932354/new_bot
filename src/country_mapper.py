def detect_region_country(text):

    text = text.lower()

    # ======================
    # 🇦🇸 ASIA
    # ======================
    if "philippines" in text or "philippine" in text:
        return "🇵🇭 필리핀"

    elif "japan" in text:
        return "🇯🇵 일본"

    elif "indonesia" in text:
        return "🇮🇩 인도네시아"

    elif "malaysia" in text:
        return "🇲🇾 말레이시아"

    elif "vietnam" in text:
        return "🇻🇳 베트남"

    elif "thailand" in text:
        return "🇹🇭 태국"

    elif "bangladesh" in text:
        return "🇧🇩 방글라데시"

    elif any(x in text for x in ["asia", "asian"]):
        return "🌏 기타 아시아국가"


    # ======================
    # 🌎 LATIN AMERICA
    # ======================
    elif "peru" in text:
        return "🇵🇪 페루"

    elif "chile" in text:
        return "🇨🇱 칠레"

    elif "colombia" in text:
        return "🇨🇴 콜롬비아"

    elif "argentina" in text:
        return "🇦🇷 아르헨티나"

    elif "mexico" in text:
        return "🇲🇽 멕시코"

    elif "brazil" in text:
        return "🇧🇷 브라질"

    elif any(x in text for x in ["latin america", "latam"]):
        return "🌎 기타 중남미"

    return "🌍 기타"