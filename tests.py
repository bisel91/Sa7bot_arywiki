from datetime import date

import pywikibot


def date_of_birth_format(year, month, day):
    if not year:
        return None  # Return None if year is not provided
    if not month:
        month = 1  # Default to January if month is not provided
    if not day:
        day = 1  # Default to the 1st day if day is not provided
    return date(year, month, day)
def is_date_multiple(entity_id, property):
    try:
        wikidata_site = pywikibot.Site("wikidata", "wikidata")
        item = pywikibot.ItemPage(wikidata_site, entity_id)
        item.get()
        date_claims = item.claims.get(property, [])
        if len(date_claims) > 1:
            # Filter statements by rank (preferred or normal)
            preferred_statements = [s for s in date_claims if s.rank == 'preferred']
            normal_statements = [s for s in date_claims if s.rank == 'normal']
            deprecated_statements = [s for s in date_claims if s.rank == 'deprecated']
            y1 = date_claims[0].getTarget()
            y2 = date_claims[1].getTarget()
            if y1.year == y2.year:
                return False
            elif preferred_statements and normal_statements:
                return False
            else:
                if normal_statements and deprecated_statements:
                    return False
                else:
                    print("25")
                    return True
        else:
            return False
    except:
        print("Exception is date multiple")


def get_date_wikidata(id, property):
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
                    return date_of_birth_format(year, month, day)
                else:
                    date_of_ = normal_statements[0].getTarget()
                    year = date_of_.year
                    month = date_of_.month
                    day = date_of_.day
                    return date_of_birth_format(year, month, day)
            else:
                date_of_ = date_claim[0].getTarget()
                year = date_of_.year
                month = date_of_.month
                day = date_of_.day
                return date_of_birth_format(year, month, day)
        else:
            return None
    except pywikibot.exceptions.NoPage as e:
        print(f"The item with QID {id} does not exist.")
    except Exception as e:
        print("An error occurred:", e)


def get_gender_of_human_item(item_id):
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
def get_country_id(article_title):
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
        return "Country of citizenship not found"
def get_demonym_from_wikidata(items_id:[]):
    #print(len(items_id))
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
    try:
        gender = get_gender_of_human_item('Q204487')
        #print("gender:", gender)
        nats=[]
        for item_id in items_id:
            #print(item_id)
            item = pywikibot.ItemPage(repo, item_id)
            item.get()
            if "P1549" in item.claims:
                demonym_claim = item.claims["P1549"]
                nationalities=[]
                for dc in demonym_claim:
                    if dc.getTarget().language == 'ary':
                        nat = dc.getTarget().text
                        nationalities.append(nat)
                if gender == 'female':
                    nats.append(nationalities[1])
                else:
                    nats.append(nationalities[0])
        return nats
        print(f"No demonym found for item {item_id}")
    except IndexError as e:
        print(f"An IndexError occurred: {e}")
    except AttributeError as ae:
        print("AttributeError:",ae)
    return None



print('nationalities:',get_demonym_from_wikidata(get_country_id("زين لعابدين بنعلي")))
# You can access the selected statement's value using selected_statement.mainsnak
