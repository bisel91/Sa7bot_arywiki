import json
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import ollama
from pypdf import PdfReader


# ---------------------------------------------------------
# 1. Define the Structured Target Schema
# ---------------------------------------------------------
class DocumentData(BaseModel):
    document_title: str = Field(description="Title or heading of the document")
    author_or_organization: str = Field(description="Author, company, or publisher")
    summary: str = Field(description="A 2-3 sentence overview of the content")
    key_findings: list[str] = Field(description="Key metrics, dates, or takeaways")


# ---------------------------------------------------------
# 2. Helper: Scrape PDF Links from a Webpage
# ---------------------------------------------------------
def scrape_pdf_urls(webpage_url: str) -> list[str]:
    """Finds all hyperlinks ending in .pdf on a target webpage."""
    response = requests.get(webpage_url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    pdf_urls = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.lower().endswith(".pdf"):
            pdf_urls.append(urljoin(webpage_url, href))

    return list(set(pdf_urls))


# ---------------------------------------------------------
# 3. Helper: Read Text from Local or Remote PDF
# ---------------------------------------------------------
def extract_text_from_pdf(pdf_source: str) -> str:
    """Extracts raw text from a local filepath or web URL."""
    if pdf_source.startswith(("http://", "https://")):
        response = requests.get(pdf_source, stream=True, timeout=15)
        response.raise_for_status()
        temp_path = "_temp.pdf"
        with open(temp_path, "wb") as f:
            f.write(response.content)

        reader = PdfReader(temp_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        os.remove(temp_path)
        return text
    else:
        reader = PdfReader(pdf_source)
        return "\n".join([page.extract_text() or "" for page in reader.pages])


# ---------------------------------------------------------
# 4. Core Pipeline: Extract Data via Ollama
# ---------------------------------------------------------
def process_pdfs(pdf_list: list[str], model_name: str = "llama3.2") -> list[dict]:
    results = []

    for idx, pdf_item in enumerate(pdf_list, start=1):
        print(f"[{idx}/{len(pdf_list)}] Processing: {pdf_item}")
        try:
            # Step A: Parse PDF text
            raw_text = extract_text_from_pdf(pdf_item)
            if not raw_text.strip():
                print(f"Skipping {pdf_item}: No readable text found.")
                continue

            # Step B: Prompt Ollama with Pydantic JSON Schema
            prompt = f"Extract structured data strictly according to the target schema:\n\n{raw_text[:8000]}"

            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                format=DocumentData.model_json_schema()
            )

            # Step C: Validate output into Pydantic model
            parsed_record = DocumentData.model_validate_json(response.message.content)

            record_dict = parsed_record.model_dump()
            record_dict["source"] = pdf_item
            results.append(record_dict)

        except Exception as e:
            print(f"Error processing {pdf_item}: {e}")

    return results


# ---------------------------------------------------------
# 5. Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    # Option A: Scrape links directly from a site
    # pdf_sources = scrape_pdf_urls("https://example.com/reports")

    # Option B: Manual list of local or remote paths
    pdf_sources = [
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        # "sample_document.pdf"
    ]

    # Process PDFs using local LLM model
    extracted_data = process_pdfs(pdf_sources, model_name="llama3.2")

    # Output to structured JSON file
    output_filename = "extracted_pdf_data.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)

    print(f"\nDone! Extracted {len(extracted_data)} documents into '{output_filename}'.")