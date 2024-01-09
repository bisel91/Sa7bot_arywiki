from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot
from arywiki import Article
categories=[
    'زيادة  1986',
    'زيادة  1987',
    'زيادة  1988',
    'زيادة  1989',
    'زيادة  1990',
    'زيادة  1991'

]
def deathInfoProcessing(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in categories:
        catg = pywikibot.Category(site, cat)
        print(catg.title())
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 100):
            art = Article(page.title())
            print(page.title(), ":")
            content = art.get_main_content()
            section0 = page.text.split("==")[0]
            section1 = page.text.split("==")[1]
            section2 =page.text.split("==")[2]
            dateofdeath =None
            if art.extract_date_of_death(section0) != None:
                dateofdeath =art.extract_date_of_death(section0)
                print("Date of death(WIKIPEDIA) SEC0:", art.extract_date_of_death(section0))
            elif art.extract_date_of_death(section1 )!=None:
                dateofdeath = art.extract_date_of_death(section1)
                print("Date of death(WIKIPEDIA) SEC1", dateofdeath)
            else:
                dateofdeath = art.extract_date_of_death(section2)
                print("Date of death(WIKIPEDIA) SEC2", dateofdeath)
            date_death_fromWikiData = art.get_date_wikidata(art.get_qid(page.title()), "P570")
            if date_death_fromWikiData!=None:
                print("Date of death(WIKIDATA):", date_death_fromWikiData)
            elif dateofdeath!=None:
                qid =art.get_qid(art.articleTitle)
                art.save_to_excel([qid, "P569", dateofdeath] ,'dates_birth_death')
            else:
                print("Still Alive")
            if all(item is not None for item in [date_death_fromWikiData, dateofdeath]):
                # إلى تاريخ الوفاة فيها كتر من تاريخ د لوفاة
                # multiplicity2 = art.is_date_multiple(art.get_qid(page.title()), "P570")
                equality =art.compare_wikipedia_to_wikidata(dateofdeath ,date_death_fromWikiData)
                if equality is False:
                    precision_wikidata =art.get_date_precision(art.get_qid(page.title()) ,"P570")
                    print("Precision(wikidata)" ,precision_wikidata)
                    precision_ary = art.get_precision_of_any_date(dateofdeath)
                    print("Precision(ary)" ,precision_ary)
                    if precision_wikidata>=9 and precision_ary<= precision_wikidata:
                        print("line 553")
                        newd =art.formated_date_of_birth(date_death_fromWikiData)
                        oldd =art.formated_date_of_birth(dateofdeath)
                        art.update_date_of_birth(page.title() ,oldd ,newd ,precision_ary ,"P570")
        print("-------------------------------------------")
deathInfoProcessing(categories)