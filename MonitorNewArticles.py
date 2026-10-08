import pywikibot


def process_new_articles(lang='ary', limit=20):
    # الاتصال بويكيبيديا (الدارجة)
    site = pywikibot.Site(lang, 'wikipedia')

    print(f"🔍 جاري جلب آخر {limit} مقالات جديدة...")
    print("=" * 50)

    # namespaces=0 باش نجيبو غير المقالات العادية (تجاهل التصنيفات والقوالب)
    new_articles = site.newpages(namespaces=0, total=limit)

    for page in new_articles:
        title = page.title()

        # استخراج معلومات على أول نسخة (شكون أنشأ المقالة وإمتى)
        first_revision = page.oldest_revision
        creator = first_revision.user
        creation_time = first_revision.timestamp

        # طباعة معلومات المقالة
        print(f"📄 المقالة: {title}")
        print(f"👤 الكاتب: {creator}")
        print(f"🕒 تاريخ الإنشاء: {creation_time.strftime('%Y-%m-%d %H:%M')}")

        # --------------------------------------------------
        # هنا تقدر تزيد المهام لي بغيتي البوت يديرها فالمقالة
        # --------------------------------------------------

        # 1. مثلا: تزيد ليها تاريخ الازدياد إيلا كانت ديال شي شخصية
        # update_birth_date_from_wikidata(title, lang)

        # 2. أو دير ليها تصحيح إملائي
        # fix_spelling_and_formatting(title, lang)

        print("-" * 50)


# تشغيل السكريبت (غادي يجيب آخر 10 مقالات)
if __name__ == "__main__":
    process_new_articles(lang='ary', limit=10)