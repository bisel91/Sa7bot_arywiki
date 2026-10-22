from firecrawl import Firecrawl

app = Firecrawl(api_key="fc-YOUR-API-KEY")

schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_facts": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["title", "summary"]
}

result = app.scrape(
    "https://en.wikipedia.org/wiki/Marie_Curie",
    formats=[{"type": "json", "schema": schema}]
)

print(result["json"])