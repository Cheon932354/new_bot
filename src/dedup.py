import json
import os

FILE_PATH = "data/sent_articles.json"

def load_sent_articles():

    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:
        return json.load(f)

def is_duplicate(link):

    sent_articles = load_sent_articles()

    return link in sent_articles

def save_article(link):

    sent_articles = load_sent_articles()

    sent_articles.append(link)

    with open(FILE_PATH, "w") as f:
        json.dump(sent_articles, f, indent=2)