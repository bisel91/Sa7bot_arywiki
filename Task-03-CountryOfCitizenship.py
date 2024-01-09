from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot

from arywiki import Article


def countryprocessing(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in categories:
        print("**************", cat, "***********************")
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 100):
            art = Article("")
            art.articleTitle = page.title()
            print(art.articleTitle, ":")
            print("nationality :", art.get_demonym_from_wikidata(art.get_country_id(art.articleTitle)))
            art.search_demonym_into_text(art.get_demonym_from_wikidata(art.get_country_id(art.articleTitle)))
        print("---------------------------------")
categories2=[
    'كتاب مغاربة'
]
countryprocessing(categories2)