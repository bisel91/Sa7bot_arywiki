import pywikibot

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

QID = "Q101190967"  # replace with your item
item = pywikibot.ItemPage(repo, QID)
item.get()

def add_monolingual_claim(item, prop_id, text, language):
    claim = pywikibot.Claim(repo, prop_id)
    target = pywikibot.WbMonolingualText(text=text, language=language)
    claim.setTarget(target)
    item.addClaim(claim, summary=f"Adding {prop_id} via pywikibot")
    print(f"Added {prop_id}: {text} ({language})")

# Female form of label (P2521)
add_monolingual_claim(item, "P2521", "مصورة طيران", "ary")  # example value/lang

# Male form of label (P3321)
add_monolingual_claim(item, "P3321", "مصور طيران", "ary")  # example value/lang