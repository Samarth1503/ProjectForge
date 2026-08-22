from projectforge.ai.provider import AIProvider, AIResponse
from projectforge.ai.gemini import GeminiProvider

def get_provider(config) -> AIProvider:
    """Factory to get the configured AI provider."""
    return GeminiProvider(
        api_key=config.gemini_api_key.get_secret_value(),
        model=config.projectforge_model,
        temperature=config.projectforge_temperature,
        max_output_tokens=config.projectforge_max_output_tokens,
        max_retries=config.projectforge_max_retries,
        timeout=config.projectforge_request_timeout,
    )

__all__ = ["AIProvider", "AIResponse", "GeminiProvider", "get_provider"]
