import pywikibot
import re


def is_person(page):
    """
    هاد الدالة كترجع True إيلا كانت المقالة كتهضر على شخص
    """
    try:
        item = pywikibot.ItemPage.fromPage(page)
        if item.exists():
            item.get()
            if 'P31' in item.claims:
                for claim in item.claims['P31']:
                    target = claim.getTarget()
                    if target and target.id == 'Q5':
                        return True
    except pywikibot.exceptions.NoPageError:
        pass

    text = page.text
    person_infoboxes = r'\{\{\s*(معلومات شخص|صندوق معلومات شخص|معلومات ممثل|معلومات كاتب|معلومات لاعب|معلومات سياسي)'
    if re.search(person_infoboxes, text):
        return True
    if re.search(r'\[\[(تصنيف|Category):مواليد\s+\d+', text):
        return True

    return False


def process_new_people_articles(lang='ary', limit=50):
    site = pywikibot.Site(lang, 'wikipedia')

    print(f"🔍 جاري البحث فآخر {limit} مقالة جديدة لاستخراج مقالات الأشخاص...")
    print("=" * 50)

    new_articles = site.newpages(namespaces=0, total=limit)

    people_found = 0

    # 🔴 التعديل تدار هنا: غادي نفصلو الـ Tuple لـ page و معلومات إضافية
    for item in new_articles:
        page = item[0]  # كنجبدو الصفحة من الـ Tuple
        title = page.title()

        if is_person(page):
            people_found += 1

            # حيت جبدنا الصفحة، دابا نقدر نخدمو عادي
            creator = page.oldest_revision.user

            print(f"👤 لقيت مقالة ديال شخص: {title}")
            print(f"✍️ الكاتب: {creator}")
            print("-" * 30)

    print(f"✅ ساليت! لقيت {people_found} مقالة ديال أشخاص من أصل {limit} مقالة جديدة.")


if __name__ == "__main__":
    process_new_people_articles(lang='ary', limit=50)