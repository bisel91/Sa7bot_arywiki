import requests
import urllib.parse


def get_subcategories(category_name, lang="ary"):
    url = f"https://{lang}.wikipedia.org/w/api.php"

    # ويكيبيديا الدارجة تنظم التصنيفات ببادئة "تصنيف:"
    if not category_name.startswith("تصنيف:") and not category_name.startswith("Category:"):
        category_name = f"تصنيف:{category_name}"

    headers = {
        "User-Agent": "WikiCategoryFetcher/1.0 (https://ary.wikipedia.org/)"
    }

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmtype": "subcat",  # جلب التصنيفات الفرعية فقط
        "cmlimit": "max",
        "format": "json"
    }

    subcategories = []

    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"خطأ في الطلب: {response.status_code}")
            break

        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])

        for member in members:
            subcategories.append(member["title"])

        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break

    return subcategories


if __name__ == "__main__":
    # أسماء التصنيفات الشائعة للشخصيات في ويكيبيديا الدارجة
    categories_to_try = ["علماء","مواليد","وفيات","فقهاء","كتاتبيا","أكاديميين_مغاربا","مومتيلات_د_لأفلام_مغريبيات"]

    for cat_name in categories_to_try:
        print(f"جاري البحث في التصنيف: '{cat_name}'...")
        results = get_subcategories(cat_name)

        if results:
            print(f"\nتم العثور على {len(results)} تصنيف فرعي داخل 'تصنيف:{cat_name}':\n")
            for cat in results:
                print(cat)
            break
        else:
            print(f"لم يتم العثور على تصنيفات فرعية داخل 'تصنيف:{cat_name}'.\n")