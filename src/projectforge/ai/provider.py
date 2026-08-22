from typing import Protocol, Optional
from pydantic import BaseModel

class AIResponse(BaseModel):
    """Normalized response from any AI provider."""
    text: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    finish_reason: Optional[str] = None

class AIProvider(Protocol):
    """Protocol defining the interface for AI providers."""
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 4096,
    ) -> AIResponse:
        ...
