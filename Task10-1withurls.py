import json
import os
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import ollama


# ==========================================
# 1. DEFINE YOUR EXTRACTION SCHEMA
# ==========================================
class WebPageData(BaseModel):
    title: str = Field(..., description="Main heading or title of the page")
    summary: str = Field(..., description="A 2-3 sentence summary of the key content")
    key_entities: list[str] = Field(..., description="List of key topics, technologies, or entities mentioned")


# ==========================================
# 2. HELPER: SCRAPE & CLEAN HTML
# ==========================================
def scrape_clean_text(url: str, timeout: int = 15) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Strip unnecessary HTML nodes to conserve VRAM
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    # Extract non-empty text lines
    lines = (line.strip() for line in soup.get_text().splitlines())
    cleaned_text = "\n".join(chunk for chunk in lines if chunk)

    # Truncate text context length to 5,000 characters to prevent OOM
    return cleaned_text[:5000]


# ==========================================
# 3. HELPER: OLLAMA EXTRACTION
# ==========================================
def extract_with_qwen(text: str, model_name: str = "qwen2.5:3b") -> dict:
    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction assistant. Output raw valid JSON strictly adhering to the schema."
            },
            {
                "role": "user",
                "content": f"Extract target data from this website content:\n\n{text}"
            }
        ],
        format=WebPageData.model_json_schema(),  # Enforces Pydantic schema validation
        options={
            "temperature": 0.0,
            "num_ctx": 4096
        }
    )
    return json.loads(response["message"]["content"])


# ==========================================
# 4. MAIN BATCH PROCESSOR
# ==========================================
def process_urls_from_file(file_path: str="urls.txt", output_file: str = "results.json", model_name: str = "qwen2.5:3b"):
    if not os.path.exists(file_path):
        print(f"[!] File '{file_path}' not found.")
        return

    # Read URLs line by line, stripping whitespace & empty lines
    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[*] Found {len(urls)} URLs to process.\n")
    results = []

    for index, url in enumerate(urls, 1):
        print(f"[{index}/{len(urls)}] Processing: {url}")
        try:
            raw_text = scrape_clean_text(url)
            extracted_data = extract_with_qwen(raw_text, model_name=model_name)

            record = {
                "url": url,
                "status": "success",
                "data": extracted_data
            }
            print(f"  └─ Successfully extracted: {extracted_data.get('title', 'N/A')}")

        except Exception as e:
            print(f"  └─ Error processing {url}: {e}")
            record = {
                "url": url,
                "status": "error",
                "error": str(e)
            }

        results.append(record)

    # Save output into a structured JSON file
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2, ensure_ascii=False)

    print(f"\n[✓] Batch complete! Results saved to '{output_file}'.")


if __name__ == "__main__":
    # Use 'qwen2.5:3b' for speed/reliability or 'qwen2.5:7b' if you have 8GB+ VRAM
    process_urls_from_file("urls.txt", output_file="extracted_data.json", model_name="qwen2.5:3b")