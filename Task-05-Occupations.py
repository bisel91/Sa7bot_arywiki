from pywikibot import pagegenerators
from pywikibot.scripts.generate_user_files import pywikibot
from arywiki import Article
categories=[
    'ناس تزادو ف الدار البيضا',
    'ناس تزادو ف الرباط',
    'ناس تزادو ف سلا',
    'ناس تزادو ف فاس'

]
categories2=[
    'كتاب مغاربة',
    'شاعير مغريبي',
    'كاتيبات مغريبيات',
    'أكاديميين مغاربا',
    'ديپلوماسي مغريبي',
    'وزير أول مغريبي',
    'وزيرة مغريبية',
    'سلطان مغريبي',
    'زريعة شخصيات د لمغريب'
]
birthsof=[
    'زيادة  1905',
    'زيادة  1906',
    'زيادة  1907',
    'زيادة  1908',
    'زيادة  1909',
    'زيادة  1910',
    'زيادة  1911',
    'زيادة  1912',
    'زيادة  1913',
    'زيادة  1914',
    'زيادة  1915',
    'زيادة  1916'
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
def get_occupation_ByTitle(item_id):
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    occupations_claim = item.claims['P106']

    occupations = []
    for claim in occupations_claim:
        male_label = claim.target.labels.get('ary', '')

        # Use P2521 to get the female form of the label
        female_claim = claim.target.claims.get('P2521')

        female_label = female_claim[0]
        print(female_label)

        if male_label:
            occupations.append(male_label)
        if female_label:
            occupations.append(female_label)

    return occupations
def get_occupations_ByList(categories):
    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in categories:
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        for page in pagegenerators.PreloadingGenerator(pages, 15):
            try:
                art = Article("")
                art.articleTitle = page.title()
                item = pywikibot.ItemPage.fromPage(page)
                # Get the claims for the 'occupations' property (P106)
                occupations_claim = item.claims['P106']
                occupations = [claim.target.get()['labels'].get('ary', '') for claim in occupations_claim]
                return occupations
            except KeyError:
                return None
print(get_occupation_ByTitle('Q131117'))