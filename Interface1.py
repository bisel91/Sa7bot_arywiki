from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

WIKI_API = "https://ary.wikipedia.org/w/api.php"

def get_articles_by_date(date_str, category):
    # Convert date to MediaWiki format
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    start = date_obj.strftime("%Y-%m-%dT00:00:00Z")
    end = (date_obj + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    params = {
        "action": "query",
        "format": "json",
        "list": "recentchanges",
        "rcstart": end,
        "rcend": start,
        "rctype": "new",
        "rcnamespace": 0,
        "rclimit": 50
    }

    response = requests.get(WIKI_API, params=params)
    data = response.json()

    articles = []

    for change in data.get("query", {}).get("recentchanges", []):
        title = change["title"]

        # Check category membership
        cat_params = {
            "action": "query",
            "format": "json",
            "prop": "categories",
            "titles": title,
            "cllimit": 50
        }

        cat_response = requests.get(WIKI_API, params=cat_params)
        cat_data = cat_response.json()

        pages = cat_data.get("query", {}).get("pages", {})
        for page_id in pages:
            categories = pages[page_id].get("categories", [])
            for cat in categories:
                if category.lower() in cat["title"].lower():
                    articles.append(title)

    return articles


@app.route("/", methods=["GET", "POST"])
def index():
    articles = []
    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        articles = get_articles_by_date(date, category)

    return render_template("index.html", articles=articles)


if __name__ == "__main__":
    app.run(debug=True)