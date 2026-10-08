import asyncio
import os
import json
from pprint import pprint
import requests
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CrawlResult
)
from sqlalchemy.pool.dbapi_proxy import proxies

# ----------------------------
# DeepSeek API Key
# ----------------------------
DEEPSEEK_KEY = os.getenv("sk-fbf006fbb9cb4d3cad6927bba45a857b")
if not DEEPSEEK_KEY:
    raise ValueError("DeepSeek API key not found in environment variable")
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"
EXTRACTION_SCHEMA = {
    "games": [
        {
            "id": "number",
            "title": "string",
            "url": "string|null",
            "genres": ["string"],
            "description": "string|null",
            "price": "string|null",
            "action": "string|null"
        }
    ]
}


# ----------------------------
# Function to send markdown to DeepSeek
# ----------------------------
def extract_with_deepseek(markdown_text):
    system_instruction = (
        "You are a structured data extractor. "
        "Extract only game data from the given markdown text. "
        "Return a clean JSON object that matches the provided schema exactly. "
        "Do not include any explanations or markdown formatting. "
        "Use null for missing values."
    )

    schema_msg = {
        "role": "system",
        "content": "Schema:\n" + json.dumps(EXTRACTION_SCHEMA, indent=2)
    }

    user_msg = {"role": "user", "content": markdown_text}

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_instruction},
            schema_msg,
            user_msg
        ],
        "temperature": 0.0,
        "max_tokens": 2000
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(DEEPSEEK_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]

        # Clean JSON code block markers if present
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")  # remove all backticks
            cleaned = cleaned.replace("json", "", 1).strip()  # remove 'json' if present

        # Try to parse cleaned content as JSON
        try:
            parsed = json.loads(cleaned)
            print("\n✅ Parsed JSON successfully!\n")
            return parsed
        except json.JSONDecodeError as je:
            print(f"[DeepSeek ERROR] Failed to decode JSON: {je}")
            return None
    except Exception as e:
        print(f"[DeepSeek ERROR] {e}")
        return None


# ----------------------------
# Main async crawler & extraction
# ----------------------------
async def main():
    browser_config = BrowserConfig(headless=True, verbose=True)
    async with AsyncWebCrawler(config=browser_config, proxy=proxies["http"]) as crawler:
        crawler_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
        )

        url = "https://sandbox.oxylabs.io/products"
        result = await crawler.arun(url=url, config=crawler_config)

        # ----------------------------
        # Handle both CrawlResult object or string
        # ----------------------------
        if hasattr(result.markdown_v2, "raw_markdown"):
            markdown_text = result.markdown_v2.raw_markdown
        else:
            markdown_text = str(result.markdown_v2)

        # ----------------------------
        # Call DeepSeek to extract structured JSON
        # ----------------------------
        extracted = extract_with_deepseek(markdown_text)
        if extracted:
            print("DeepSeek Extracted Data:")
            print(json.dumps(extracted, indent=2))
            with open("products_deepseek.json", "w", encoding="utf-8") as f:
                json.dump(extracted, f, indent=2)
            print("Data saved to products_deepseek.json")
        else:
            print("DeepSeek extraction failed")


if __name__ == "__main__":
    asyncio.run(main())
