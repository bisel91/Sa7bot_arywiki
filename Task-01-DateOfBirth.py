from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot

from arywiki import Article

categories1=[
    'ناس تزادو ف سلا'
]
categories=[
    'ناس تزادو ف الدار البيضا',
    'ناس تزادو ف الرباط',
    'ناس تزادو ف سلا',
    'ناس تزادو ف فاس'

]
categories2=[
    'مغنية بتاشلحيت',
    'مغني بتاشلحيت'
]
birthsof=[
    'زيادة  1940',
    'زيادة  1941',
    'زيادة  1942',
    'زيادة  1943',
    'زيادة  1944',
    'زيادة  1945',
    'زيادة  1946',
    'زيادة  1947'
]
births=[
    'زيادة  1893',
    'زيادة  1894',
    'زيادة  1895',
    'زيادة  1896',
    'زيادة  1897',
    'زيادة  1898',
    'زيادة  1899',
    'زيادة  1900',
    'زيادة  1901',
    'زيادة  1902',
    'زيادة  1903',
    'زيادة  1904'
]
births2=[
    'زيادة  1881',
    'زيادة  1882',
    'زيادة  1883',
    'زيادة  1884',
    'زيادة  1885',
    'زيادة  1886',
    'زيادة  1887',
    'زيادة  1888',
    'زيادة  1889',
    'زيادة  1890',
    'زيادة  1891',
    'زيادة  1892'
]
births3=[
    'زيادة  1869',
    'زيادة  1870',
    'زيادة  1871',
    'زيادة  1872',
    'زيادة  1873',
    'زيادة  1874',
    'زيادة  1875',
    'زيادة  1876',
    'زيادة  1877',
    'زيادة  1878',
    'زيادة  1879',
    'زيادة  1880'
]
births4=[
    'وفيات  1857',
    'وفيات  1858',
    'وفيات  1859',
    'وفيات  1860',
    'وفيات  1861',
    'وفيات  1862',
    'وفيات  1863',
    'وفيات  1864',
    'وفيات  1865',
    'وفيات  1866',
    'وفيات  1867',
    'وفيات  1868'
]

def ByListOfCategory(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in categories:
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 20):
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
ByListOfCategory(categories2)
