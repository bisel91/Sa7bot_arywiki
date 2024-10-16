from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot

from arywiki import Article

categories = [
        'ناس تزادو ف رباط',
        'فيلسوف يوناني',
        'فيلسوف',
        'شوعارا ؤ شاعرات مغاربة',
        'رساما مغاربة',
        'فيلسوف مغريبي',
        'توارخي مغريبي',
        'كتاب رحالا مغاربا',
        'شخصيات دينية مغريبية',
        'صحافيين ؤ صحافيات مغاربا',
        'ضباط د لبوليس مغاربا',
        'طباخ مغريبي',
        'فنانا ؤ فنانات د لكوميكس مغاربا',
        'فنانين ؤ فنانات مغاربا',
        'مهنديسين مغاربا',
        'ناس قراو ف ليسي ديكارط'
        'زيادة 1963',
        'كوايري جزايري',
        'كوايري بلجيكي',
        'كوايري فرانساوي',
        'كوايري مغريبي',
        'زيادة  1943',
        'زيادة  1944',
        'زيادة  1945',
        'زيادة  1946',
        'زيادة  1947',
        'زيادة  1948',
        'رايس د لميريكان',
        'ناس تزادو ف الدار البيضا',
        'ناس تزادو ف فاس',
        'ناس تزادو ف مراكش',
        'ناس تزادو ف طانجا',
        'ناس تزادو ف سل',
        'ناس تزادو ف مكناس'
    ]

def ByListOfCategory(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in categories:
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 100):
            try:
                art = Article("")
                art.articleTitle = page.title()
                print(art.articleTitle, ":")
                content = art.get_main_content()
                # date of birth from wikipedia
                date_fromPage = art.get_date_from_article(content)
                # date of death from wikipedia
                if date_fromPage == None:
                    if page.text.split('\n\n')[0].__contains__(art.formated_date_of_birth(
                            art.get_date_wikidata(art.get_entity_fromArticle(), "P569"))):
                        date_fromPage = art.get_date_wikidata(art.get_entity_fromArticle(), "P569")
                print("Date of birth(WIKIPEDIA):", date_fromPage)
                date_fromWikiData = art.get_date_wikidata(art.get_entity_fromArticle(), "P569")
                print("Date of birth(WIKIDATA):", date_fromWikiData)
                # print("Occupation:",self.get_occupations_from_wikidata())
                # الدقة ديال تاريخ الازدياد
                precision = art.get_date_precision(art.get_entity_fromArticle(), "P569")
                wikiprec = art.get_precision_of_any_date(date_fromPage)
                # إلى ويكيداتا فيها كثر من تاريخ ديال الازدياد
                multiplicity = art.is_date_multiple(art.get_entity_fromArticle(), "P569")
                if multiplicity:
                    print("Multiplicity BRTHDate:", multiplicity)
                else:
                    equality = art.compare_wikipedia_to_wikidata(date_fromPage, date_fromWikiData)
                    if not equality and wikiprec != None:
                        if precision >= 9 and wikiprec <= precision:
                            print("Precision wikidata", art.get_date_precision(art.get_entity_fromArticle(), "P569"))
                            print("precision wikipedia", wikiprec)
                            newdate = art.formated_date_of_birth(date_fromWikiData)
                            oldate = art.formated_date_of_birth(date_fromPage)
                            art.update_date_of_birth(art.articleTitle, oldate, newdate, wikiprec, "P569")
            except pywikibot.exceptions.NoPageError as ep:
                row = [art.articleTitle, date_fromPage, '0000-00-00']
                art.save_to_excel(row, 'Not_existing_entity')
                print("Added to excel file successfully")
        print("-------------------------------------------")
ByListOfCategory(categories)
