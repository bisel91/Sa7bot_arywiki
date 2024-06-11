#TESTS
import json
import logging
from urllib.error import HTTPError, URLError
import re
from urllib.parse import quote, urljoin

import gspread
import pywikibot
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2 import service_account
#from oauth2client.service_account import ServiceAccountCredentials

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

        def has_property_(self,wikidata_item_id,p):
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            item = pywikibot.ItemPage(repo, wikidata_item_id)
            item.get()
            if p in item.claims:
                print(wikidata_item_id," Has property:",p)
                return True
            else:
                print(wikidata_item_id, " Has not property:", p)
                return False
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
            if not self.has_property_(item_id,'P214'):
                self.retrieve_nresult_fromAF(art.get_wikidata_label(item_id), 'VIAF ID')
            # identifiers, wikidata_link = self.extract_identifiers(item_id)
            # datav=art.get_wikidata_label(item_id)
            # if identifiers:
            #       print("-----------VERIFICATION OF IDENTIFIERS--------")
            #       for prop, data in identifiers.items():
            #           print("DATA VALUE:", datav)
            #           #print("Property:",prop," |Ref:",data['reference'],"| Value:",data['value'])
            #           if prop!='VIAF ID':
            #               print("This Item has no VIAF ID")
            #               self.retrieve_nresult_fromAF(datav, 'VIAF ID')
            #           if prop!='ISNI':
            #               self.retrieve_nresult_fromAF(datav,'ISNI')
            #           if prop!='Bibliothèque nationale de France ID':
            #               self.retrieve_nresult_fromAF(datav, 'BnF')
            #           if prop!='GND ID':
            #               self.retrieve_nresult_fromAF(datav, 'GND ID')
            #           if prop!='SBN author ID':
            #               self.retrieve_nresult_fromAF(datav, 'SBN')
            #           if prop!='FAST ID':
            #               self.retrieve_nresult_fromAF(datav, 'FAST ID')
            #           if prop!='Allcinema person ID':
            #               print("")
            #           if prop!='AllMovie person ID':
            #               print("")
            #           if prop!='AllMusic artist ID':
            #               print("")
            #           if prop!='AlloCiné person ID':
            #               print("")
            #           if prop!='BBC Things ID':
            #               print("")
            #           if prop!='Freebase ID':
            #               print("")
            #           if prop!="ResearchGate contributions ID":
            #               print("")
            # else:
            #       print(f"Item {item_id} is not an instance of human (Q5) or has no identifiers.")

        def save_to_excel(self,rows):
            try:
                print("-----------Saving into Excel--------")
                scope = ["https://spreadsheets.google.com/feeds",
                         'https://www.googleapis.com/auth/spreadsheets',
                         "https://www.googleapis.com/auth/drive.file",
                         "https://www.googleapis.com/auth/drive"]
                #credentials = ServiceAccountCredentials.from_service_account_file('creds.json')
                #service_account_info = json.loads('creds.json')
                with open('creds.json') as f:
                    service_account_info = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(service_account_info)
                #scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds_with_scope = credentials.with_scopes(scope)
                gc = gspread.authorize(creds_with_scope)
                spreadsheet = gc.open("Missing_references").sheet1
                #sh = gc.open_by_key()
                spreadsheet.append_row(rows, value_input_option='RAW')
                print("Row added successfully.")
            except Exception as e:
                print(f"Error: {e}")

        def getid_fromurl(self,url):
            match = re.search(r'/(\d+)/', url)
            if match:
                desired_number = match.group(1)
                return desired_number
            else:
                return None

        def the_appropriate_link(self,link):
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            entry1=soup.find('h2',id='nameEntry1')
            content=entry1.get_text()
            print("content:",content)


        def get_people_without_property(self):
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            # SPARQL query to get people from Morocco without ISNI (P214)
            query = """
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
              ?item wdt:P27 wd:Q1028;  # Instance of: Human, Country: Morocco
                    MINUS { ?item wdt:P214 [] }  # Exclude items with ISNI (P214)
              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            LIMIT 700
            """
            generator = pagegenerators.PreloadingEntityGenerator(
                pagegenerators.WikidataSPARQLPageGenerator(query, site=repo))
            for item in generator:
                if 'en' in item.labels:
                    self.retrieve_nresult_fromAF(item.getID(),item.labels['en'],'VIAF ID')
        def retrieve_nresult_fromAF(self,qid,name,af):
            print("-----------SCRAPPING DATA FROM AUTHORITY FILES--------")
            print("NAME:",name,"|| ID:",af)
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
                    #viaf_url=soup.find('td','recName')
                    viaf_url=soup.find_all(attrs={'class': 'recName'})
                    if num_found_viaf:
                        num_found_content = num_found_viaf.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_content)
                        if match:
                            extracted_number = match.group(1)
                            print("VIAF Occurences:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                base_url="https://viaf.org"
                                for vl in viaf_url:
                                  href= vl.find('a')
                                  if href:
                                      relative_path = href.get('href')
                                      full_url=urljoin(base_url,quote(relative_path))
                                      print("URL=",full_url)
                                      if name in full_url:
                                          print("This is the right URL")
                                          viaf_id = self.getid_fromurl(full_url)
                                          self.save_to_excel([qid,name,"birthdate",'P214','VIAF ID',viaf_id])
                                          # if art.get_wikidata_label(qid) in self.extract_name_and_dates(full_url):
                                          #   print("[",qid,name,"birthdate",'P214','VIAF ID',viaf_id,"]")
                                #text inside tag a
                                #print("date of birth:",)
                                    # qid = art.get_qid(art.articleTitle)
                                    # print("ITEM WIKIDATA ID:", qid)
                                    # idw = "WKP-" + qid
                                    # response2 = requests.get(full_url)
                                    # soup2 = BeautifulSoup(response2.text, 'html.parser')
                                    # wikidata_element = soup2.find('a', id=idw)
                                    # viaf_id = self.getid_fromurl(full_url)
                                    # print("REF", viaf_id, "\n")
                                    # property = 'P214'
                                    # property_name = 'VIAF ID'
                                    # if wikidata_element:
                                    #     print("it is the same element as wikidata")
                                    #     print("ID", qid, "\n")
                                    #     print("PROPERTY", 'P214', "\n")
                                    #     self.save_to_excel([qid, property, property_name, viaf_id])
                                    # else:
                                    #     self.save_to_excel([qid, property, property_name, viaf_id])
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
                                response2=requests.get("https://isni.oclc.org/cbs/DB=1.2/SET=1/TTL=1/SHW?FRST=1&TRM=douglas+adams")
                                soup2 = BeautifulSoup(response2.text, 'html.parser')
                                td_rec_title = soup.find('td', class_='rec_title')  # inside
                                divtag=td_rec_title.find('div')
                                spantag=divtag.find('span')
                                isnid=spantag.get_text()
                                print("ISNI ID=",isnid)
                                propisni = 'P213'
                                property_name = 'ISNI'
                                self.save_to_excel([qid, propisni, property_name, isnid])
                        else:
                            print("No number found in the content.")
                else:
                    print("Failed to retrieve the webpage. Status code:", response.status_code)
            elif af=='BnF':
                response = requests.get(urlbnf)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    num_found_bnf = soup.find('ul', class_='pages')
                    if num_found_bnf:
                        nb=num_found_bnf.find('span',class_='nbPage')
                        num_found_bnf_content=nb.get_text()
                        match = re.search(r'\b(\d+)\b', num_found_bnf_content)
                        if match:
                            extracted_number = match.group(1)
                            print("BnF:", int(extracted_number))
                            if int(extracted_number) >= 1:
                                qid = art.get_qid(art.articleTitle)
                                propbnf = 'P268'
                                property_name = 'Bibliothèque nationale de France ID'
                                ref = urlbnf
                                self.save_to_excel([qid, propbnf, property_name, ref])
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
                                td_tag=soup.find(id='tableRecordData_0')
                                base_url = "https://portal.dnb.de/"
                                relative_path = td_tag.find('a').get('href')
                                full_url = urljoin(base_url, quote(relative_path))
                                response2 = requests.get(full_url)
                                soup2 = BeautifulSoup(response2.text, 'html.parser')
                                table=soup2.find(id='fullRecordTable')
                                ahref=table.find('a').get('href')
                                ref=self.getid_fromurl(ahref)
                                qid = art.get_qid(art.articleTitle)
                                propgnd = 'P227'
                                property_name = 'GND ID'
                                self.save_to_excel([qid, propgnd, property_name, ref])
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
                                href=soup.find('td',class_='recName')
                                fastID=href.find('a').get('href')
                                propfast = 'P2163'
                                property_name = 'FAST ID'
                                self.save_to_excel([qid, propfast, property_name, fastID])
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
    categories = [
        'زيادة  1972',
        'زيادة  1973',
        'زيادة  1974',
        'زيادة  1975',
        'زيادة  1976',
        'زيادة  1977',
        'زيادة  1978',
        'زيادة  1979',
        'زيادة  1980',
        'زيادة  1981',
        'زيادة  1982',
        'زيادة  1983',
        'زيادة  1984',
        'زيادة  1985',
        'زيادة  1986',
        'زيادة  1987',
        'زيادة  1988',
        'زيادة  1989',
        'زيادة  1990',
        'زيادة  1991'
    ]
    categories2 = [
        'زريعة شخصيات د لمغريب'
    ]

    family = 'wikipedia'
    lang = 'ary'
    site = pywikibot.Site(lang, family)
    art = Article("")
    ref = Reference(art)
    ref.get_people_without_property()
    # for cat in categories2:
    #     catg = pywikibot.Category(site, cat)
    #     pages = catg.articles()
    #     print(cat.title())
    #     for page in pagegenerators.PreloadingGenerator(pages, 20):
    #         try:
    #             art = Article("")
    #             art.articleTitle = page.title()
    #             ref = Reference(art)
    #             print(art.articleTitle)
    #             #ref.verify_AF(art.get_qid(art.articleTitle))
    #             ref.get_people_without_property()
    #         except Exception as ex:
    #             print("Message",ex)