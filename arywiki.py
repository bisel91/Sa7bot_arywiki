import pywikibot
import requests
import re
from pywikibot import pagegenerators,textlib
from datetime import date
from pywikibot.textlib import extract_sections
from pywikibot.config import usernames
from pywikibot.exceptions import PageRelatedError


class Article:
    # initializing the variables
    selected_section=0
    keywordexpressionb=""
    keywordexpressiond = ""
    articleTitle = ""
    ARY_MONTHS=[" يناير ", " فبراير ", " مارس ", " أبريل ", " ماي ", " يونيو "," يوليوز ", " غشت ", " شتنبر "," أكتوبر ", " نونبر ", " دجنبر "]
    was_born_keywords = ["تزاد",
                         "تزادت",
                         "تولد",
                         "تولدات",
                         "خلاق",
                         "خلاقت",
                         "مزيودة",
                         "مزيود",
                         "تزاد عام",
                         "تزادت عام",
                         "تولد عام",
                         "تولدات عام",
                         "خلاق عام",
                         "خلاقت عام",
                         "مزيودةعام",
                         "مزيود عام",
                         "تزاد نهار",
                         "تزادت نهار",
                         "تولد نهار",
                         "تولدات نهار",
                         "خلاق نهار",
                         "خلاقت نهار",
                         "مزيودة نهار",
                         "مزيود نهار",
                         "تزاد ف",
                         "تزادت ف",
                         "تولد ف",
                         "تولدات ف",
                         "خلاق ف",
                         "خلاقت ف",
                         "مزيودة ف",
                         "مزيود ف"]
    was_dead_keywords=[
        "مات ف",
        "مات",
        "توفا ف",
        "توفّا",
        "ماتت ف",
        "ماتت",
        "توفات ف",
        "توفّات",
        "توفّى ف",
        "مات نهار",
        "ماتت نهار",
        "توفا نهار",
        "توفات نهار",
        "توفّا نهار",
        "توفّات نهار",
        "توفّى نهار",
        "مات عام",
        "ماتت عام",
        "توفا عام",
        "توفات عام",
        "توفّا عام",
        "توفّات عام",
        "توفّى عام",
        "مات سنة",
        "ماتت سنة",
        "توفا سنة",
        "توفات سنة",
        "توفّا سنة",
        "توفّات سنة",
        "توفّى سنة"

    ]
    def __init__(self,articletitle):
        super().__init__()
        self.articleTitle=articletitle
    def extract_date_of_death(self,text):
        keywords_pattern = "|".join(map(re.escape, self.was_dead_keywords))
        months_pattern = "|".join(map(re.escape, self.ARY_MONTHS))
        date_pattern = f'({keywords_pattern})\s*?(\d*)\s*({months_pattern})\s*(\d*)'
        match = re.search(date_pattern, text)
        year = None
        month = None
        day = None
        try:
            ntext=match.group()
            for keyword in self.was_dead_keywords:
                if keyword in ntext:
                    year_match = re.search(r'\d{4}', ntext)
                    if year_match:
                        year = int(year_match.group())
                        ntext = ntext.replace(year_match.group(), '', 1)  # Remove year from the text
                    for month_name in self.ARY_MONTHS:
                        if month_name in ntext:
                            month = self.ARY_MONTHS.index(month_name) + 1
                            ntext = ntext.replace(month_name, '', 1)  # Remove month from the text
                    day_match = re.search(r'\d{1,2}', ntext)
                    if day_match:
                        day = int(day_match.group())
                    break  # Exit the loop if a keyword is found
        except Exception as e:
            print("Exception extracting death date")
        return self.date_of_birth_format(year,month,day)

    def get_country_id(self,article_title):
        site = pywikibot.Site("ary", 'wikipedia')
        page = pywikibot.Page(site, article_title)
        # Fetch the Wikidata item linked to the page
        item = pywikibot.ItemPage.fromPage(page)
        item_dict = item.get()
        # Extract the "country of citizenship" value from Wikidata
        if 'P27' in item_dict['claims']:
            citizenship_claims = item_dict['claims']['P27']
            countries_id=[]
            for cc in citizenship_claims:
                citizenship_target = cc.getTarget()
                qid = citizenship_target.id
                countries_id.append(qid)
            return countries_id
        else:
            return None

    def get_demonym_from_wikidata(self,items_id: []):
        # print(len(items_id))
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()
        try:
            if items_id:
                gender = self.get_gender_of_human_item(self.get_qid(self.articleTitle))
                # print("gender:", gender)
                nats = []
                for item_id in items_id:
                    # print(item_id)
                    item = pywikibot.ItemPage(repo, item_id)
                    item.get()
                    if "P1549" in item.claims:
                        demonym_claim = item.claims["P1549"]
                        nationalities = []
                        for dc in demonym_claim:
                            if dc.getTarget().language == 'ary':
                                nat = dc.getTarget().text
                                nationalities.append(nat)
                        if gender == 'female':
                            nats.append(nationalities[1])
                        else:
                            nats.append(nationalities[0])
                return nats
            else:
                return "No demonym found for item"
        except IndexError as e:
            print(f"An IndexError occurred: {e}")
        except AttributeError as ae:
            print("AttributeError:", ae)
        return None
    def get_date_from_article(self,gtext):
            ntext=self.extract_date_regex(gtext)
            year = None
            month = None
            day = None
            if ntext==None:
                return None
            else:
                try:
                    for keyword in self.was_born_keywords:
                        if keyword in ntext:
                            self.keywordexpressionb=keyword
                            year_match = re.search(r'\d{4}', ntext)
                            if year_match:
                                year = int(year_match.group())
                                ntext = ntext.replace(year_match.group(), '', 1)  # Remove year from the text
                            for month_name in self.ARY_MONTHS:
                                if month_name in ntext:
                                    month = self.ARY_MONTHS.index(month_name) + 1
                                    ntext = ntext.replace(month_name, '', 1)  # Remove month from the text
                            day_match = re.search(r'\d{1,2}', ntext)
                            if day_match:
                                day = int(day_match.group())
                            break  # Exit the loop if a keyword is found
                except:
                    print("exception")
                return self.date_of_birth_format(year,month,day)
    def extract_date_regex(self,text):
            pattern = r"^(.*?\d{4})"
            pattern_marge= r"تولد ما بين \d{4} و \d{4}"
            matched = re.search(pattern, text)
            matched_marge = re.search(pattern_marge, text)
            if matched_marge is not None:
                return None
            elif matched is not None:
                extracted_text = matched.group(1)
                print("Extracted text:", extracted_text)
                return extracted_text
            else:
                return None
    def date_of_birth_format(self,year,month,day):
        if not year:
            return None  # Return None if year is not provided
        if not month:
            month = 1  # Default to January if month is not provided
        if not day:
            day = 1  # Default to the 1st day if day is not provided
        return date(year, month, day)
    def month_number(self,monthname):
        MONTH_TO_NUMBER = {
           "يناير" :1,
           "فبراير" :2,
           "مارس" :3,
           "أبريل" :4,
           "ماي" :5,
           "يونيو" :6,
           "يوليوز" :7,
           "غشت" :8,
           "شتنبر" :9,
           "أكتوبر" :10,
           "نونبر" :11,
           "دجنبر" :12

        }
        return MONTH_TO_NUMBER.get(monthname)
    def get_main_content(self):
        base_url = "https://ary.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": self.articleTitle,
            "prop": "extracts",
            "exintro": True,      # المقدمة فين كيكون تاريخ الازدياد
            "explaintext": True,
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        #print(data)
        try:
            # Check if the 'extract' key exists in the response
            # Extract the page content from the response JSON
            page_id = list(data["query"]["pages"].keys())[0]
            main_content = data["query"]["pages"][page_id]["extract"]
        except KeyError:
            # Handle the case when the 'extract' key is not present in the response
            return None
        return main_content

    def get_category_pages(self,category_name):
        site= pywikibot.Site("ary", "wikipedia")  # invoke English Wikipedia
        category = pywikibot.Category(site, category_name)
        gen = pagegenerators.CategorizedPageGenerator(category, recurse=True)
        return list(gen)
    def get_entity_fromArticle(self): #
        try:
            site = pywikibot.Site("ary", "wikipedia")
            page = pywikibot.Page(site, self.articleTitle)
            item = pywikibot.ItemPage.fromPage(page)
            qid = item.getID()
            return qid
        except:
            print("ENTITY NOT FOUND")
    def get_qid(self,title): #
        try:
            site = pywikibot.Site("ary", "wikipedia")
            page = pywikibot.Page(site, title)
            item = pywikibot.ItemPage.fromPage(page)
            qid = item.getID()
            return qid
        except:
            print("ENTITY NOT FOUND")

    def is_date_multiple(self,entity_id,property):
        try:
            wikidata_site = pywikibot.Site("wikidata", "wikidata")
            item = pywikibot.ItemPage(wikidata_site, entity_id)
            item.get()
            date_claims = item.claims.get(property, [])
            if len(date_claims) > 1:
                # Filter statements by rank (preferred or normal)
                preferred_statements = [s for s in date_claims if s.rank == 'preferred']
                normal_statements = [s for s in date_claims if s.rank == 'normal']
                deprecated_statements=[s for s in date_claims if s.rank == 'deprecated']
                y1=date_claims[0].getTarget()
                y2=date_claims[1].getTarget()
                if y1.year==y2.year:
                    return False
                elif preferred_statements and normal_statements:
                    return False
                else:
                    if normal_statements and deprecated_statements:
                        return False
                    elif preferred_statements and deprecated_statements:
                        return False
                    else:
                        if property=="P569":
                            self.add_page_to_category("[[تصنيف:شخصيات عندها كتر من تاريخ د الزيادة ف ويكيداطا]]")
                        else: #P570
                            self.add_page_to_category("[[تصنيف:شخصيات عندها كتر من تاريخ د لوفاة ف ويكيداطا]]")
                        return True
            else:
                return False
        except:
            print("Exception is date multiple")
    def get_date_wikidata(self,id,property):
        try:
            # Input validation
            if not id or not property:
                raise ValueError("Invalid ID or property")
            wikidata_site = pywikibot.Site("wikidata", "wikidata")
            item = pywikibot.ItemPage(wikidata_site, id)
            if not item.exists():
                return None  # Handle the case where the item does not exist
            item.get()
            date_claim = item.claims.get(property, [])
            year, month, day = None, None, None
            if date_claim:
                preferred_statements = [s for s in date_claim if s.rank == 'preferred']
                normal_statements = [s for s in date_claim if s.rank == 'normal']
                deprecated_statements = [s for s in date_claim if s.rank == 'deprecated']

                if len(date_claim) > 1:
                    if (preferred_statements and normal_statements) or (preferred_statements and deprecated_statements):
                        date_of_ = preferred_statements[0].getTarget()
                        year = date_of_.year
                        month = date_of_.month
                        day = date_of_.day
                        return self.date_of_birth_format(year, month, day)
                    else:
                        date_of_ = normal_statements[0].getTarget()
                        year = date_of_.year
                        month = date_of_.month
                        day = date_of_.day
                        return self.date_of_birth_format(year, month, day)
                else:
                    date_of_ = date_claim[0].getTarget()
                    year = date_of_.year
                    month = date_of_.month
                    day = date_of_.day
                    return self.date_of_birth_format(year, month, day)
            else:
                return None
        except pywikibot.exceptions.NoPageError as e:
              print(f"The item with QID {id} does not exist.")
        except Exception as e:
            print("An error occurred:", e)
    def get_date_precision(self,entityid,property):
        try:
            if not id or not property:
                raise ValueError("Invalid ID or property")
            # Set up a pywikibot site (you may need to configure your site)
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            item = pywikibot.ItemPage(repo, entityid)
            item.get()
            # Specify the date of birth property (P569)
            date_of_birth_property_id = property

            date_claims = item.claims.get(date_of_birth_property_id,[])
            # Retrieve the date of birth claim
            if date_claims:
                preferred_statements = [s for s in date_claims if s.rank == 'preferred']
                normal_statements = [s for s in date_claims if s.rank == 'normal']
                deprecated_statements = [s for s in date_claims if s.rank == 'deprecated']
                if len(date_claims) > 1:
                    if (preferred_statements and normal_statements) or (preferred_statements and deprecated_statements):
                        date_target =preferred_statements[0].getTarget()
                        precision = date_target.precision
                        return precision
                    else:
                        date_target = normal_statements[0].getTarget()
                        precision = date_target.precision
                        return precision
                else:
                    # Extract the first claim (assuming there's only one date of birth claim)
                    date_claim = date_claims[0]
                    # Get the target value, which includes precision information
                    date_target = date_claim.getTarget()
                    # Get the precision of the date of birth
                    precision = date_target.precision
                    return precision
            else:
                print("No date of birth claim found for this item.")

        except pywikibot.exceptions.Error:
         print("Page wikidata doesn't exist.")
        except Exception as e:
            print("Other exceptions")
    def display_categories(article_title):
        site= pywikibot.Site("ary", "wikipedia")  # invoke English Wikipedia
        page = pywikibot.Page(site, article_title)
        categories = page.categories()
    def compare_wikipedia_to_wikidata(self,wikipedia_birthday,wikidata_birthday):
        if wikipedia_birthday==wikidata_birthday:
            return True
        else:
            return False
    def formated_date_of_birth(self,wiki_date:date):
        # Initialize empty strings for day and month
        day_str = ""
        month_str = ""
        year_str=""
        d=""
        try:
            if wiki_date.day>1:
                day_str = str(wiki_date.day)
                d+=day_str+" "
                month_str = self.date_to_text(wiki_date.month)
                d+= month_str + " "
                year_str = str(wiki_date.year)
                d+= year_str
            elif wiki_date.day==1 and self.date_to_text(wiki_date.month)=="يناير":
                d+=str(wiki_date.year)
            else:
                month_str = self.date_to_text(wiki_date.month)
                d += month_str + " "
                year_str = str(wiki_date.year)
                d += year_str
        except:
         print("")
        return d
    def get_precision_of_any_date(self,wiki_date:date):
        if wiki_date!=None:
            if wiki_date.day > 1 :
                return 11
            elif wiki_date.day == 1 and wiki_date.month==1:
                return 9
            else:
                return 10
        else:
            return None
    def date_to_text(self,monthnumber):
        MONTH_TO_NUMBER = {
           1 :"يناير",
           2 :"فبراير",
           3 :"مارس",
           4 :"أبريل",
           5 :"ماي",
           6 :"يونيو",
           7 :"يوليوز",
           8 :"غشت",
           9 :"شتنبر",
           10 :"أكتوبر",
           11 :"نونبر",
           12 :"دجنبر"

        }
        return MONTH_TO_NUMBER.get(monthnumber)
    def add_page_to_category(self,category_to_add):
        site = pywikibot.Site("ary", "wikipedia")
        page = pywikibot.Page(site, self.articleTitle)
        # Check if the category is already on the page
        if category_to_add not in page.text:
            site.login()
            page.text+="\n"+category_to_add
            # Save the page with a summary
            summary = f" تصنيف جديد:{category_to_add}"
            page.save(summary=summary)
            print(f"Category '{category_to_add}' added to the article '{page.title()}'.")
        else:
            print(f"Category '{category_to_add}' is already on the article '{page.title()}'.")

    def remove_4_digit_numbers(self,text):
        # Define the regex pattern to match 4-digit numbers
        pattern = r'\b\d{4}\b'  # \b ensures whole word matching
        # Use re.sub to remove all occurrences of 4-digit numbers
        modified_text = re.sub(pattern, '', text)
        return modified_text

    def get_gender_of_human_item(self,item_id):
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()
        item = pywikibot.ItemPage(repo, item_id)
        item.get()
        if "P31" in item.claims:
            for claim in item.claims["P31"]:
                if claim.target.id == "Q5":  # Q5 is the Wikidata item for "human"
                    if "P21" in item.claims:
                        for gender_claim in item.claims["P21"]:
                            gender_id = gender_claim.target.id
                            gender_item = pywikibot.ItemPage(repo, gender_id)
                            gender_item.get()
                            return gender_item.labels["en"] if "en" in gender_item.labels else None
        return None
    def update_date_of_birth(self,title,oldate,newdate,pre,property):
        try:
            if oldate!=None:
                site = pywikibot.Site("ary", "wikipedia")
                site.login()
                page = pywikibot.Page(site, title)
                # Retrieve the current content of the article
                page_text = page.text
                # Split the content into sections
                sections = page_text.split('\n\n')
                # Check if there is at least one section
                result = extract_sections(page_text, site)
                if oldate in sections[0]:
                    self.selected_section=0
                elif oldate in sections[1]:
                    self.selected_section=1
                else:
                    self.selected_section=2
                sec1 = sections[self.selected_section]
                description=""
                if property=="P569":
                    description="تبدال ديال تاريخ دالزيادة"
                else:
                    description="تبدال ديال تاريخ دالوفاة"
                if sections:
                    prewikidata=self.get_date_precision(self.get_entity_fromArticle(),property)
                    alterdate="1 يناير "+oldate
                    if prewikidata==11 and pre==9:
                        if alterdate in sec1:
                            new_article_text = re.sub(alterdate, newdate, sec1)
                            print(oldate, "-Line 349-", newdate)
                            # print(new_article_text)
                            sections[self.selected_section] = new_article_text
                            updated_page_text = '\n\n'.join(sections)
                            page.text = updated_page_text
                            save_result = page.save(summary=description, minor=False, botflag=True,force=True)
                            print("save result:", save_result)
                        else:
                            exp1="عام "+"[["+oldate+"]]"
                            exp11 = "عام " + oldate
                            target1="نهار "+newdate
                            wd=self.remove_4_digit_numbers(target1)
                            patt=wd+"[["+oldate+"]]"
                            pattern = re.compile(re.escape(exp1), re.IGNORECASE)
                            if exp1 in sec1:
                                print(exp1, "-Line 332-", patt)
                                new_article_text = re.sub(pattern, patt, sec1)
                                #print(pattern)
                                #print(new_article_text)
                                sections[self.selected_section]= new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                                print("save result:",save_result)
                            elif exp11 in sec1:
                                new_article_text = re.sub(exp1, target1, sec1)
                                print(exp1, "-Line 341-", exp1)
                                #print(new_article_text)
                                sections[self.selected_section]= new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                                print("save result:",save_result)
                            else:
                                new_article_text = re.sub(oldate, newdate, sec1)
                                print(oldate, "-Line 349-",newdate)
                                #print(new_article_text)
                                sections[self.selected_section]= new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                                print("save result:", save_result)
                    elif prewikidata==10 and pre==9:
                        exp2="عام "+"[["+oldate+"]]"
                        exp22="عام "+oldate
                        target2="شهر "+newdate
                        dw=self.remove_4_digit_numbers(target2)
                        patt = dw+ "[[" + oldate + "]]"
                        pattern = re.compile(re.escape(exp2), re.IGNORECASE)
                        if exp2 in sec1:
                            new_article_text = re.sub(pattern, patt, sec1)
                            print(exp2, "-Line 360-",target2)
                            #print(new_article_text)
                            sections[self.selected_section]= new_article_text
                            updated_page_text = '\n\n'.join(sections)
                            page.text = updated_page_text
                            save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                            print("save result:", save_result)
                        elif exp22 in sec1:
                            new_article_text=re.sub(exp22,target2,sec1)
                            print(exp22, "-Line 360-", target2)
                            #print(new_article_text)
                            sections[self.selected_section]= new_article_text
                            updated_page_text = '\n\n'.join(sections)
                            page.text = updated_page_text
                            save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                            print("save result:", save_result)
                        else:
                            new_article_text = re.sub(oldate, newdate, sec1)
                            print(oldate, "-Line 347-", newdate)
                            #print(new_article_text)
                            sections[self.selected_section]= new_article_text
                            updated_page_text = '\n\n'.join(sections)
                            page.text = updated_page_text
                            save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                            print("save result:", save_result)
                    else:
                        if prewikidata==11 and pre==10:
                            alter=str(1)+" "+oldate
                            target4="شهر "+oldate
                            target5 = "نهار " + newdate
                            if alter in sec1:
                                new_article_text = re.sub(alter, newdate, sec1)
                                sections[self.selected_section] = new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True,force=True)
                                print("save result:", save_result)
                            elif target4 in sec1:
                                new_article_text = re.sub(target4, target5, sec1)
                                sections[self.selected_section] = new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True,
                                                        force=True)
                                print("save result:", save_result)
                            else:
                                new_article_text = re.sub(oldate, newdate, sec1)
                                print(oldate, "-Line 355-",newdate)
                                #print(new_article_text)
                                #print(sections[0])
                                sections[self.selected_section]= new_article_text
                                updated_page_text = '\n\n'.join(sections)
                                page.text = updated_page_text
                                save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                                print("save result:", save_result)
                        else:
                            new_article_text = re.sub(oldate, newdate, sec1)
                            print(oldate, "-Line 355-", newdate)
                            # print(new_article_text)
                            # print(sections[0])
                            sections[self.selected_section] = new_article_text
                            updated_page_text = '\n\n'.join(sections)
                            page.text = updated_page_text
                            save_result = page.save(summary=description, minor=False, botflag=True, force=True)
                            print("save result:", save_result)

        except pywikibot.exceptions.EditConflictError as e:
                print("Edit conflict occurred. Please resolve manually:", e)
        except pywikibot.exceptions.NoUsernameError as e:
                print("No username configured for the bot:", e)
        except Exception as e:
                    print("An error occurred while updating:", e)
        except pywikibot.exceptions.OtherPageSaveError as err:
              print("Edit to page ",err)
    def deathInfoProcessing(self,categories):
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
                section2=page.text.split("==")[2]
                dateofdeath=None
                if art.extract_date_of_death(section0) != None:
                    dateofdeath=art.extract_date_of_death(section0)
                    print("Date of death(WIKIPEDIA) SEC0:", art.extract_date_of_death(section0))
                elif art.extract_date_of_death(section1)!=None:
                    dateofdeath = art.extract_date_of_death(section1)
                    print("Date of death(WIKIPEDIA) SEC1", dateofdeath)
                else:
                    dateofdeath = art.extract_date_of_death(section2)
                    print("Date of death(WIKIPEDIA) SEC2", dateofdeath)
                print("Calling GET_DATE_WIKIDATA")
                date_death_fromWikiData = art.get_date_wikidata(art.get_qid(page.title()), "P570")
                if date_death_fromWikiData!=None:
                    print("Date of death(WIKIDATA):", date_death_fromWikiData)
                else:
                    print("Date of death not existing in wikidata")
                if all(item is not None for item in [date_death_fromWikiData, dateofdeath]):
                    # إلى تاريخ الوفاة فيها كتر من تاريخ د لوفاة
                    # multiplicity2 = art.is_date_multiple(art.get_qid(page.title()), "P570")
                     equality=art.compare_wikipedia_to_wikidata(dateofdeath,date_death_fromWikiData)
                     if equality is False:
                         precision_wikidata=art.get_date_precision(art.get_qid(page.title()),"P570")
                         print("Precision(wikidata)",precision_wikidata)
                         precision_ary = art.get_precision_of_any_date(dateofdeath)
                         print("Precision(ary)",precision_ary)
                         if precision_wikidata>=9 and precision_ary<=precision_wikidata:
                             print("line 553")
                             newd=art.formated_date_of_birth(date_death_fromWikiData)
                             oldd=art.formated_date_of_birth(dateofdeath)
                             art.update_date_of_birth(page.title(),oldd,newd,precision_ary,"P570")
            print("-------------------------------------------")


    def birthInfoProcessing(self,categories):
        family = 'wikipedia'
        lang = 'ary'
        site = pywikibot.Site(lang, family)
        for cat in categories:
            catg = pywikibot.Category(site, cat)
            pages = catg.articles()
            for page in pagegenerators.PreloadingGenerator(pages, 10):
                self.articleTitle=page.title()
                print(self.articleTitle, ":")
                content = self.get_main_content()
                # date of birth from wikipedia
                date_fromPage = self.get_date_from_article(content)
                # date of death from wikipedia
                if date_fromPage == None:
                    if page.text.split('\n\n')[0].__contains__(self.formated_date_of_birth(
                            self.get_date_wikidata(self.get_entity_fromArticle(), "P569"))):
                        date_fromPage = self.get_date_wikidata(self.get_entity_fromArticle(), "P569")
                print("Date of birth(WIKIPEDIA):", date_fromPage)
                date_fromWikiData = self.get_date_wikidata(self.get_entity_fromArticle(), "P569")
                print("Date of birth(WIKIDATA):", date_fromWikiData)
                try:
                    # الدقة ديال تاريخ الازدياد
                    precision = self.get_date_precision(self.get_entity_fromArticle(), "P569")
                except pywikibot.exceptions.NoWikibaseEntityError:
                    print("Entity doesn't exist on wikidata:wikidata")
                wikiprec = self.get_precision_of_any_date(date_fromPage)
                # إلى ويكيداتا فيها كثر من تاريخ ديال الازدياد
                multiplicity = self.is_date_multiple(self.get_entity_fromArticle(), "P569")
                if multiplicity:
                    print("Multiplicity BRTHDate:", multiplicity)
                else:
                    equality = self.compare_wikipedia_to_wikidata(date_fromPage, date_fromWikiData)
                    try:
                        if not equality and wikiprec != None:
                            if precision >= 9 and wikiprec <= precision:
                                print("Precision wikidata",self.get_date_precision(self.get_entity_fromArticle(), "P569"))
                                print("precision wikipedia", wikiprec)
                                newdate = self.formated_date_of_birth(date_fromWikiData)
                                oldate = self.formated_date_of_birth(date_fromPage)
                                self.update_date_of_birth(self.articleTitle, oldate, newdate, wikiprec,"P569")
                    except Exception as e:
                        print(e)
            print("-------------------------------------------")
    def search_demonym_into_text(self,demonyms:[]):
        site = pywikibot.Site("ary", "wikipedia")
        page = pywikibot.Page(site, self.articleTitle)
        content = page.text
        if demonyms is not None:
            print(self.get_main_content())
            for d in demonyms:
                 if (d in self.get_main_content()):
                     print("GOOD!")
                 else:
                     print("You should add",d)
        else:
            print("ما كاينة حتى جنسية فهاد لارتيكل ولا مكتوبة بالغلط")
    def updateCountryOfCitizenship(self,oldc,newc):
        site = pywikibot.Site("ary", "wikipedia")
        site.login()
        page = pywikibot.Page(site, self.articleTitle)
        page_text = page.text
        sections = page_text.split('\n\n')
        result = extract_sections(page_text, site)
        sec1 = sections[0]
        new_article_text = re.sub(oldc, newc, sec1)
        # print(new_article_text)
        sections[0] = new_article_text
        updated_page_text = '\n\n'.join(sections)
        page.text = updated_page_text
        description="تصحيح ولا تبدال ديال بلد الجنسية"
        save_result = page.save(summary=description, minor=False, botflag=True, force=True)
        print("save result:", save_result)
    def countryprocessing(self,categories):
        family = 'wikipedia'
        lang = 'ary'
        site = pywikibot.Site(lang, family)
        for cat in categories:
            print("**************",cat,"***********************")
            catg = pywikibot.Category(site, cat)
            pages = catg.articles()
            for page in pagegenerators.PreloadingGenerator(pages, 100):
                self.articleTitle=page.title()
                print(self.articleTitle, ":")
                print("nationality :",self.get_demonym_from_wikidata(self.get_country_id(self.articleTitle)))
                self.search_demonym_into_text(self.get_demonym_from_wikidata(self.get_country_id(self.articleTitle)))
            print("---------------------------------")
#TESTS
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
    'زيادة 1930',
    'زيادة 1931',
    'زيادة 1932',
    'زيادة 1933',
    'زيادة 1934',
    'زيادة 1935',
    'زيادة 1936',
    'زيادة 1937',
    'زيادة 1938',
    'زيادة 1939',
    'زيادة 1940',
    'زيادة 1941'
]
art=Article("")
art.deathInfoProcessing(birthsof)









