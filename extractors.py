from crawl4ai import LLMExtractionStrategy, LLMConfig
from schemas import PropertyModel  # Pydantic model (optional)


def get_llm_extractor():
    llm_config = LLMConfig(
        provider="groq/llama3-70b",  # Or "openai/gpt-4"
        api_key="llmapi_e5641f9e33a4218deba0ece4406bbc03339b8ef4f650a1c67ff017c8fe976e21",
    )

    return LLMExtractionStrategy(
        llm_config=llm_config,
        schema=PropertyModel.model_json_schema(),
        instruction="Extract property date of birth, position, and city.",
    )