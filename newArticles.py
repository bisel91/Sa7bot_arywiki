import pywikibot
import re
# Set up the site and page
site = pywikibot.Site('ary', 'wikipedia')  # Change 'en' and 'wikipedia' if you're working with a different language/site
page_title = 'ريم فكري'  # Replace with the actual page title you want to check
page = pywikibot.Page(site, page_title)
# Get the text content of the page
page_text = page.text
# Compile a regex pattern to find <ref> tags and their contents
ref_pattern = re.compile(r'<ref\b[^>]*>(.*?)</ref>', re.IGNORECASE | re.DOTALL)
# Find all <ref> tags
refs = ref_pattern.findall(page_text)
# Check if any of the <ref> tags contain the word "Morocco"
contains_word = False
for ref in refs:
    if 'Imane' in ref:
        contains_word = True
        break
if contains_word:
    print("At least one <ref> tag contains the word 'Morocco'.")
else:
    print("No <ref> tags contain the word 'Morocco'.")




