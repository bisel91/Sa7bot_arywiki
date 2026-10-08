import pywikibot
def find_weak_arabic_articles(keywords, max_results=20, min_length=2000):
    """
    Find Arabic Wikipedia articles about given topics that have poor content.
    Returns pages that are short or marked as stubs, with full URLs.
    """
    site = pywikibot.Site("ar", "wikipedia")
    results = []

    for keyword in keywords:
        search_results = site.search(keyword, total=max_results)
        for page in search_results:
            try:
                page_obj = pywikibot.Page(site, page.title())
                text = page_obj.text.strip()
                if not text:
                    continue

                # Filter: short text or "بذرة" (stub marker)
                if len(text) < min_length or "بذرة" in text:
                    page_url = page_obj.full_url()
                    results.append({
                        "title": page.title(),
                        "length": len(text),
                        "url": page_url
                    })
            except Exception as e:
                print(f"⚠️ خطأ في معالجة الصفحة {page.title()}: {e}")
                continue

    return results


if __name__ == "__main__":
    keywords = [
        "كتب الأطفال", "قصص للأطفال", "قصص اطفال", "أدب الأطفال",
        "حكايات الأطفال", "قصص خيالية للأطفال", "كتب مصورة للأطفال",
        "حكايات قبل النوم", "القصص الشعبية للأطفال", "قصص تعليمية للأطفال",
        "قصص تربوية", "قصص قصيرة للأطفال", "مجلات الأطفال"
    ]

    weak_articles = find_weak_arabic_articles(keywords, max_results=10)

    print("\n=== صفحات ويكيبيديا العربية حول كتب وقصص الأطفال التي تحتاج إلى تحسين ===\n")
    for i, article in enumerate(weak_articles, 1):
        print(f"{i}. {article['title']} (عدد الحروف: {article['length']})")
        print(f"   الرابط: {article['url']}\n")
