from typing import Optional
import time
import logging

from google import genai
from google.genai import types
from google.genai.errors import APIError

from projectforge.ai.provider import AIProvider, AIResponse
from projectforge.errors import (
    AIProviderError,
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderResponseError,
    AIProviderEmptyResponseError,
)

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    """Google Gemini implementation of the AIProvider protocol."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        max_retries: int = 3,
        timeout: int = 120,
    ):
        if not api_key:
            raise AIProviderAuthError("API key is required.")
        
        # We explicitly configure the client
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.max_retries = max_retries
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> AIResponse:
        
        final_temp = temperature if temperature is not None else self.temperature
        final_max_tokens = max_output_tokens if max_output_tokens is not None else self.max_output_tokens
        
        config = types.GenerateContentConfig(
            temperature=final_temp,
            max_output_tokens=final_max_tokens,
            system_instruction=system_prompt,
            response_mime_type="application/json"
        )
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                
                if not response.text:
                    raise AIProviderEmptyResponseError("Received empty response from Gemini.")
                    
                prompt_tokens = None
                completion_tokens = None
                if response.usage_metadata:
                    prompt_tokens = response.usage_metadata.prompt_token_count
                    completion_tokens = response.usage_metadata.candidates_token_count
                
                finish_reason = None
                if response.candidates and response.candidates[0].finish_reason:
                    finish_reason = response.candidates[0].finish_reason.name
                
                return AIResponse(
                    text=response.text,
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    finish_reason=finish_reason,
                )
                
            except APIError as e:
                status_code = getattr(e, 'code', None)
                message = getattr(e, 'message', str(e))
                
                logger.warning(f"Gemini API error (attempt {attempt + 1}/{self.max_retries + 1}): {status_code} - {message}")
                
                if status_code == 401 or status_code == 403:
                    raise AIProviderAuthError(f"Authentication failed: {message}") from e
                
                elif status_code == 429:
                    last_error = AIProviderRateLimitError(f"Rate limited: {message}")
                
                elif status_code in (500, 503, 504):
                    last_error = AIProviderResponseError(f"Server error: {message}")
                
                else:
                    raise AIProviderResponseError(f"Unexpected API error {status_code}: {message}") from e
                    
            except AIProviderError:
                raise
            except Exception as e:
                # E.g., network timeout might be raised as a different exception depending on httpx
                if "timeout" in str(e).lower():
                    last_error = AIProviderTimeoutError(f"Request timed out: {str(e)}")
                else:
                    raise AIProviderResponseError(f"Unexpected error: {str(e)}") from e
                    
            if attempt < self.max_retries:
                # Exponential backoff: 1s, 2s, 4s...
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                
        raise last_error
