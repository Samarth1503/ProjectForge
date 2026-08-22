import pytest
from projectforge.ai.gemini import GeminiProvider
from projectforge.errors import (
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderResponseError,
    AIProviderEmptyResponseError,
)
from google.genai.errors import APIError

class MockResponse:
    def __init__(self, text, prompt_tokens=None, completion_tokens=None, finish_reason=None):
        self.text = text
        class Usage:
            prompt_token_count = prompt_tokens
            candidates_token_count = completion_tokens
        self.usage_metadata = Usage() if prompt_tokens is not None else None
        
        class Candidate:
            def __init__(self, fr):
                class FR:
                    name = fr
                self.finish_reason = FR() if fr else None
        self.candidates = [Candidate(finish_reason)] if finish_reason else []

def test_gemini_provider_success(mocker):
    provider = GeminiProvider(api_key="test_key")
    
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = MockResponse(
        text='{"result": "success"}',
        prompt_tokens=5,
        completion_tokens=10,
        finish_reason="STOP"
    )
    provider.client = mock_client
    
    response = provider.generate("test prompt")
    assert response.text == '{"result": "success"}'
    assert response.prompt_tokens == 5
    assert response.completion_tokens == 10
    assert response.finish_reason == "STOP"
    assert response.model == "gemini-2.5-flash"

def test_gemini_provider_empty_response(mocker):
    provider = GeminiProvider(api_key="test_key", max_retries=0)
    
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = MockResponse(text="")
    provider.client = mock_client
    
    with pytest.raises(AIProviderEmptyResponseError):
        provider.generate("test prompt")

def test_gemini_provider_auth_error(mocker):
    provider = GeminiProvider(api_key="test_key")
    
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.side_effect = APIError(
        code=401, response_json={"error": {"message": "Invalid key"}}
    )
    provider.client = mock_client
    
    with pytest.raises(AIProviderAuthError):
        provider.generate("test prompt")

def test_gemini_provider_rate_limit_retry(mocker, monkeypatch):
    # Don't actually sleep during tests
    monkeypatch.setattr("time.sleep", lambda x: None)
    
    provider = GeminiProvider(api_key="test_key", max_retries=1)
    
    mock_client = mocker.MagicMock()
    # First call rate limits, second succeeds
    mock_client.models.generate_content.side_effect = [
        APIError(code=429, response_json={"error": {"message": "Rate limit"}}),
        MockResponse(text="Success after retry")
    ]
    provider.client = mock_client
    
    response = provider.generate("test prompt")
    assert response.text == "Success after retry"
    assert mock_client.models.generate_content.call_count == 2

def test_gemini_provider_rate_limit_exhausted(mocker, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)
    
    provider = GeminiProvider(api_key="test_key", max_retries=1)
    
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.side_effect = APIError(code=429, response_json={"error": {"message": "Rate limit"}})
    provider.client = mock_client
    
    with pytest.raises(AIProviderRateLimitError):
        provider.generate("test prompt")
    
    assert mock_client.models.generate_content.call_count == 2
