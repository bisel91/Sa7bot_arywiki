import json
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import ollama
# ==========================================
# 1. DEFINE YOUR STRUCTURED DATA SCHEMA
# ==========================================
class ArticleSchema(BaseModel):
    title: str = Field(..., description="The main heading or title of the page/article")
    author: str = Field(..., description="The author name, or 'Unknown' if not found")
    summary: str = Field(..., description="A 2-3 sentence summary of the main body text")
    key_points: list[str] = Field(..., description="A list of 3-5 main bullet points extracted from the text")
# ==========================================
# 2. FETCH & CLEAN HTML
# ==========================================
def fetch_cleaned_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # Remove non-content elements to prevent context length bloat
    for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        element.decompose()
    # Extract clean text lines
    lines = (line.strip() for line in soup.get_text().splitlines())
    cleaned_text = "\n".join(chunk for chunk in lines if chunk)
    # Truncate raw text to avoid overflowing VRAM context limits
    return cleaned_text[:6000]
# ==========================================
# 3. RUN EXTRACTION WITH OLLAMA
# ==========================================
def extract_information(url: str, model_name: str = "qwen2.5:3b"):
    print(f"[*] Fetching: {url}")
    raw_text = fetch_cleaned_text(url)

    print(f"[*] Extracting data with {model_name}...")

    # Use Pydantic json_schema to force strict validation
    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a web scraping assistant. Extract target data into the requested JSON schema strictly from the context."
            },
            {
                "role": "user",
                "content": f"Extract details from the following website text:\n\n{raw_text}"
            }
        ],
        format=ArticleSchema.model_json_schema(),  # Strict Pydantic validation schema
        options={
            "temperature": 0.0,  # Prevents output hallucination
            "num_ctx": 4096  # Allocates safe context size
        }
    )

    extracted_json = json.loads(response["message"]["content"])
    return extracted_json


# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    target_url = "https://en.wikipedia.org/wiki/Web_scraping"
    url="https://museumofmoroccanelegance.com/collection/?lang=ar"

    try:
        # Use qwen2.5:3b (or qwen2.5:7b if you have 8GB+ VRAM)
        result = extract_information(url, model_name="qwen2.5:3b")
        print("\n--- EXTRACTED JSON OUTPUT ---")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"\n[!] Scraping failed: {e}")