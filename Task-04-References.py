#TESTS
from urllib.error import HTTPError, URLError
import re
import gspread
import pywikibot
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from pywikibot import pagegenerators
import requests
from pywikibot.scripts.generate_user_files import pywikibot
from arywiki import Article
import urllib.request as urllib2
class Reference:
        art = Article("")
        def __init__(self,article):
            super().__init__()
            self.art = article
        def get_property_name(self,prop_id):
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            try:
                property_page = pywikibot.PropertyPage(repo, prop_id)
                property_page.get()
                return property_page.labels['en']
            except pywikibot.exceptions.NoPageError:
                return prop_id  # Use the property ID if the label is not available
        def extract_identifiers(self,item_id):
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            item = pywikibot.ItemPage(repo, item_id)
            item_dict = item.get()
            if 'P31' in item_dict['claims']:
                instance_of_claims = item_dict['claims']['P31']
                for claim in instance_of_claims:
                    if claim.target.id == 'Q5':  # Q5 corresponds to the 'human' item
                        identifiers = self.extract_identifiers_from_claims(item_dict['claims'])
                        return identifiers, item.title()
            return None, None
        def extract_identifiers_from_claims(self,claims):
            identifiers = {}
            for prop, values in claims.items():
                for value in values:
                    if 'P854' in value.qualifiers:
                        reference = value.qualifiers['P854'][0].getTarget()
                        reference_url = reference.full_url()
                        prop_name = self.get_property_name(prop)
                        identifiers[prop_name] = {
                            'value': value.target,
                            'reference': reference_url
                        }
                    else:
                        prop_name = self.get_property_name(prop)
                        identifiers[prop_name] = {
                            'value': value.target,
                            'reference': None
                        }
            return identifiers
        def url_ok(self,url):
            try:
                response = requests.head(url)
                # check the status code
                if response.status_code == 200:
                    return True
                else:
                    return False
            except requests.ConnectionError as e:
                return e
        item_id = 'Q42'  # Replace with the Wikidata item ID you are interested in
        def verify_AF(self,item_id):
            identifiers, wikidata_link = self.extract_identifiers(item_id)
            datav=art.get_wikidata_label(item_id)
            if identifiers:
                  print("-----------VERIFICATION OF IDENTIFIERS--------")
                  for prop, data in identifiers.items():
                      print("DATA VALUE:", datav)
                      #print("Property:",prop," |Ref:",data['reference'],"| Value:",data['value'])
                      if prop=='VIAF ID':
                          print(prop,":")
                          #return self.url_ok(f"https://viaf.org/viaf/{data['value']}/")
                      else:
                          self.retrieve_nresult_fromAF(datav,'VIAF ID')
                      if prop=='ISNI':
                          print(prop,":")
                          #return self.url_ok(f"https://isni.oclc.org/cbs/DB=1.2//CMD?ACT=SRCH&IKT=8006&TRM=ISN:{data['value']}")
                      else:
                          self.retrieve_nresult_fromAF(datav,'ISNI')
                      if prop=='Bibliothèque nationale de France ID':
                          print(prop,":")
                          #return self.url_ok(f"https://catalogue.bnf.fr/ark:/12148/{data['value']}")
                      else:
                          self.retrieve_nresult_fromAF(datav,'BnF')
                      if prop=='GND ID':
                          print(prop,":")
                          #return self.url_ok(f"https://d-nb.info/gnd/{data['value']}")
                      else:
                          self.retrieve_nresult_fromAF(datav,'GND ID')
                      if prop=='SBN author ID':
                          print(prop,":")
                          #return self.url_ok(f"https://opac.sbn.it/risultati-autori/-/opac-autori/detail/{data['value']}?core=autoriall")
                      else:
                          self.retrieve_nresult_fromAF(datav,'SBN')
                      if prop=='FAST ID':
                          print(prop,":")
                      else:
                          self.retrieve_nresult_fromAF(datav,'FAST ID')
                      if prop=='Allcinema person ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.allcinema.net/person/{data['value']}")
                      if prop=='AllMovie person ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.allmovie.com/artist/{data['value']}")
                      if prop=='AllMusic artist ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.allmusic.com/artist/{data['value']}")
                      if prop=='AlloCiné person ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.allocine.fr/personne/fichepersonne_gen_cpersonne={data['value']}.html")
                      if prop=='BBC Things ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.bbc.co.uk/things/{data['value']}")
                      if prop=='Freebase ID':
                          print(prop,":")
                          #return self.url_ok(f"https://www.google.com/search?kgmid={data['value']}")
                      if prop=="ResearchGate contributions ID":
                          print(prop,":")
                          #return self.url_ok(f"https://www.researchgate.net/scientific-contributions/{data['value']}")
            else:
                  print(f"Item {item_id} is not an instance of human (Q5) or has no identifiers.")

        def save_to_excel(self,rows):
            print("-----------Saving into Excel--------")
            scope = ["https://spreadsheets.google.com/feeds",
                     'https://www.googleapis.com/auth/spreadsheets',
                     "https://www.googleapis.com/auth/drive.file",
                     "https://www.googleapis.com/auth/drive"]
            credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open("Missing_references").sheet1
            spreadsheet.append_row(rows, value_input_option='RAW')
            print("Row added successfully.")

        def retrieve_nresult_fromAF(self,name,af):
            print("-----------SCRAPPING DATA FROM AUTHORITY FILES--------")
            # URL of the website you want to scrape
            urlviaf = f"https://viaf.org/viaf/search?query=local.personalNames%20all%20%22{name}%22&sortKeys=holdingscount&recordSchema=BriefVIAF"
            urlisni = f"https://isni.oclc.org/cbs/DB=1.2/SET=1/TTL=1/CMD?ACT=SRCH&IKT=8006&SRT=LST_nd&TRM={name}"
            urlbnf = f"https://catalogue.bnf.fr/rechercher.do;jsessionid=8850888C02760EDCA461D91EA95B3C74?motRecherche={name}&critereRecherche=0&depart=0&facetteModifiee=ok"
            urlgnd = f"https://portal.dnb.de/opac/showNextResultSite?currentResultId={name}+sortBy+ka%2Fsort.ascending%26any%26persons&currentPosition=0"
            urlfast = f"http://experimental.worldcat.org/fast/search?query=cql.any+all+%22{name}%22&stylesheet=/fast/xsl/fastresults.xsl&sortKeys=usage&maximumRecords=100&httpAccept=text/html"
            urlsnb = f"https://opac.sbn.it/en/web/opacsbn/risultati-ricerca-avanzata?monocampo={name}#1702758213573"
            #listurl = [urlviaf, urlisni, urlbnf, urlgnd, urlfast, urlsnb]
            response=None
            if af=='VIAF ID':
                response = requests.get(urlviaf)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_viaf = soup.find('div', class_='numFound')
                    viaf_url=soup.find('td','recName')
                    if num_found_viaf:

                        num_found_content = num_found_viaf.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_content)
                        year_pattern = re.compile(r'\b(\d{4})\b')
                        if match:
                            extracted_number = match.group(1)
                            print("VIAF:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                viaf_url_ = viaf_url.find('a').get('href')

                                #text inside tag a
                                dateofbirth=viaf_url.find('a',year_pattern)
                                qid = art.get_qid(art.articleTitle)
                                idw = "WKP-" + qid
                                response2 = requests.get(viaf_url_)
                                soup2 = BeautifulSoup(response2.text, 'html.parser')
                                wikidata_element = soup2.find(id=idw)
                                ar_name = wikidata_element.find('span').get_text()
                                property = 'P214'
                                lat_name=name
                                property_name = 'VIAF ID'
                                #self.save_to_excel([qid, ar_name,lat_name,dateofbirth,property, property_name, viaf_url_])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='ISNI':
                response = requests.get(urlisni)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_isn = soup.find('td', class_='result')  # inside span
                    if num_found_isn:
                        num_found_isni = num_found_isn.find('span')
                        num_found_isni_content = num_found_isni.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_isni_content)
                        if match:
                            extracted_number = match.group(1)
                            print("ISNI:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propisni = 'P213'
                                property_name = 'ISNI'
                                ref = urlisni
                               # self.save_to_excel([qid, propisni, property_name, ref])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='BnF':
                response = requests.get(urlbnf)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_bnf = soup.find('span', class_='nb')
                    if num_found_bnf:
                        num_found_bnf_content=num_found_bnf.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_bnf_content)
                        if match:
                            extracted_number = match.group(1)
                            print("BnF:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propbnf = 'P268'
                                property_name = 'BnF'
                                ref = urlbnf
                                #self.save_to_excel([qid, propbnf, property_name, ref])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='GND ID':
                response = requests.get(urlgnd)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_gn = soup.find('div', class_='searchdisplay')  # inside span classe="amount"
                    if num_found_gn:
                        num_found_gnd = num_found_gn.find('span', class_='amount')
                        num_found_gnd_content = num_found_gnd.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_gnd_content)
                        if match:
                            extracted_number = match.group(1)
                            print("GND:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propgnd = 'P227'
                                property_name = 'GND ID'
                                ref = urlgnd
                                #self.save_to_excel([qid, propgnd, property_name, ref])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='FAST ID':
                response = requests.get(urlfast)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_fastt = soup.find('div', class_='numFound')  # inside h2
                    if num_found_fastt:
                        num_found_fast = num_found_fastt.find('h2')
                        num_found_fast_content = num_found_fast.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_fast_content)
                        if match:
                            extracted_number = match.group(1)
                            print("FAST ID:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propfast = 'P2163'
                                property_name = 'FAST ID'
                                ref = urlfast
                                #self.save_to_excel([qid, propfast, property_name, ref])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='SBN':
                response = requests.get(urlsnb)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_snb = soup.find('a', class_='mx-2 btn btn-flat btn-sm btn-commons-w')
                    if num_found_snb:
                        num_found_snb_content = num_found_snb.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_snb_content)
                        if match:
                            extracted_number = match.group(1)
                            print("SNB:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propsnb = 'P396'
                                property_name = 'SBN author ID'
                                ref = urlsnb
                                #self.save_to_excel([qid, propsnb, property_name, ref])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            # Check if the request was successful (status code 200)
if __name__ == "__main__":
    birthsof = [
        'زيادة  1941',
        'زيادة  1942',
        'زيادة  1943',
        'زيادة  1944',
        'زيادة  1945',
        'زيادة  1946',
        'زيادة  1947',
        'زيادة  1948',
        'زيادة  1949',
        'زيادة  1950',
        'زيادة  1951',
        'زيادة  1952'
    ]

    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    for cat in birthsof:
        catg = pywikibot.Category(site, cat)
        pages = catg.articles()
        print(cat.title())
        for page in pagegenerators.PreloadingGenerator(pages, 20):
            try:
                art = Article("")
                art.articleTitle = page.title()
                ref = Reference(art)
                print(art.articleTitle)
                ref.verify_AF(art.get_qid(art.articleTitle))
            except Exception as ex:
                print("Message",ex)