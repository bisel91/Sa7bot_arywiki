from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot

from arywiki import Article


def countryprocessing(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    ary, ar=[], []
    for cat in categories:
        print("**************", cat, "***********************")
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 100):
            art = Article("")
            art.articleTitle = page.title()
            print(art.articleTitle, ":")
            try:
                ary, ar=art.get_demonym_from_wikidata(art.get_country_id(art.articleTitle))
                print("nationalities :",ary,ar)
                art.search_demonym_into_text(ary, ar)
            except ValueError as ve:
                print(ve)
            except TypeError as te:
                print(te)

        print("---------------------------------")
categories2=[
    'شخصيات دينية مغريبية',
    'صحافيين ؤ صحافيات مغاربا',
    'ضباط د لبوليس مغاربا',
    'طباخ مغريبي',
    'فنانا ؤ فنانات د لكوميكس مغاربا',
    'فنانين ؤ فنانات مغاربا',
    'مهنديسين مغاربا',
    'ناس قراو ف ليسي ديكارط'
    'زيادة 1963',
    'مغني مغريبي'
]
football=[
    'كوايري جزايري',
    'كوايري بلجيكي',
    'كوايري فرانساوي',
    'كوايري مغريبي'
]
professions=[
    'كتاب ألمانيين'
]
births4=[
    'ناس تزادو ف سيدي قاسم',
    'ناس تزادو ف لمحمدية',
    'ناس تزادو ف مكناس'
]
countryprocessing(categories2)