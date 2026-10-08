import pywikibot
import json
import os


def check_for_new_categories(lang='ary'):
    site = pywikibot.Site(lang, 'wikipedia')
    file_path = "known_categories.json"

    # 1. جلب التصنيفات القديمة من الملف (إيلا كاين)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            known_cats = set(json.load(f))
    else:
        known_cats = set()

    # 2. جلب كاع التصنيفات لي كاينين فويكيبيديا دابا
    print("جاري جلب التصنيفات الحالية...")
    current_cats = set(cat.title() for cat in site.allcategories())

    # 3. المقارنة باش نلقاو لي جداد
    new_cats = current_cats - known_cats

    if new_cats:
        print(f"لقيت {len(new_cats)} تصنيفات جداد:")
        for c in new_cats:
            print(c)

        # 4. تحديث الملف باش نعقلو عليهم للمرة الجاية
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(list(current_cats), f, ensure_ascii=False)
    else:
        print("ماكاين حتى تصنيف جديد.")

def monitor_new_categories(lang='ary', limit=100):
    site = pywikibot.Site(lang, 'wikipedia')

    # changetype='new' باش نجيبو غير لي عاد تنشأو
    recent_cats = site.recentchanges(namespaces=14, changetype='new', total=limit)

    for rc in recent_cats:
        print(f"تزاد تصنيف جديد: {rc['title']} من طرف {rc['user']}")


monitor_new_categories()

#check_for_new_categories()