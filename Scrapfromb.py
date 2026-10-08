import requests

GROUP_ID = "190477582867903"
ACCESS_TOKEN = "577546172733620|Th2CAFlwCRn-JGeVi4Fwh7Dhz-M"

url = f"https://graph.facebook.com/v20.0/{GROUP_ID}/feed"
params = {
    "fields": "id,message,created_time,from,permalink_url",
    "access_token": ACCESS_TOKEN
}

def get_group_posts():
    posts = []
    response = requests.get(url, params=params)

    while response.status_code == 200:
        data = response.json()
        for post in data.get("data", []):
            if "message" in post:
                posts.append({
                    "id": post["id"],
                    "author": post["from"]["name"] if "from" in post else "Unknown",
                    "message": post["message"],
                    "created_time": post["created_time"],
                    "url": post.get("permalink_url")
                })
        next_page = data.get("paging", {}).get("next")
        if next_page:
            response = requests.get(next_page)
        else:
            break
    return posts


if __name__ == "__main__":
    group_posts = get_group_posts()
    for post in group_posts:
        print(f"Author: {post['author']}")
        print(f"Time: {post['created_time']}")
        print(f"URL: {post['url']}")
        print(f"Message: {post['message']}\n{'-'*60}")
