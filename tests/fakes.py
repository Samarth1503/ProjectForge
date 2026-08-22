from typing import Optional
from projectforge.ai.provider import AIProvider, AIResponse
from projectforge.errors import AIProviderError

class FakeAIProvider(AIProvider):
    """A fake provider for testing that returns canned responses."""
    
    def __init__(self, responses: list[str | Exception]):
        """
        responses: list of strings (for successful responses) or exceptions to raise.
        """
        self.responses = responses
        self.call_count = 0
        self.calls = []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 4096,
    ) -> AIResponse:
        self.calls.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        })
        
        if self.call_count >= len(self.responses):
            # If we run out of responses, return a generic one
            resp = '{"status": "fake_success"}'
        else:
            resp = self.responses[self.call_count]
            
        self.call_count += 1
        
        if isinstance(resp, Exception):
            raise resp
            
        return AIResponse(
            text=resp,
            model="fake-model",
            prompt_tokens=10,
            completion_tokens=20,
            finish_reason="STOP"
        )
