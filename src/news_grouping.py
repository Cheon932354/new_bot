from country_mapper import detect_region_country

def group_by_country(news_list):

    grouped = {}

    for article in news_list:

        key = detect_region_country(
            article["title"] + " " + article.get("summary", "")
        )

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(article)

    return grouped