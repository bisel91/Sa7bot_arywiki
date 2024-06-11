import pywikibot


def extract_text_before_references(page_content):
    # Split the content using "==References==" as the delimiter
    sections = page_content.split("== عيون لكلام ==")
    # Use the first part before "==References==" as the extracted text
    extracted_text = sections[0].strip()

    return extracted_text


def get_wikipedia_page_content(title):
    site = pywikibot.Site("ary", "wikipedia")
    page_py = pywikibot.Page(site, title)

    if not page_py.exists():
        print(f"Page with title '{title}' does not exist.")
        return None

    return page_py.text


def main():
    # Specify the title of the Wikipedia page you want to extract text from
    wikipedia_page_title = "يوسف النصيري"

    # Get the Wikipedia page content
    page_content = get_wikipedia_page_content(wikipedia_page_title)

    if page_content:
        # Extract text before "==References=="
        extracted_text = extract_text_before_references(page_content)

        # Print or process the extracted text as needed
        print(extracted_text)


if __name__ == "__main__":
    main()





