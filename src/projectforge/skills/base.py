from abc import ABC, abstractmethod
import time
from typing import Type

from pydantic import BaseModel

from projectforge.models import ProjectContext, SkillResult
from projectforge.ai.provider import AIProvider
from projectforge.errors import SkillValidationError, SkillOutputValidationError


class BaseSkill(ABC):
    """Abstract base class for all ProjectForge skills."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier (e.g., 'requirements')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line purpose."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version string."""
        pass

    @property
    @abstractmethod
    def depends_on(self) -> list[str]:
        """Names of prerequisite skills."""
        pass

    @abstractmethod
    def get_output_schema(self) -> Type[BaseModel]:
        """Return the Pydantic model class for this skill's output."""
        pass

    @abstractmethod
    def build_prompt(self, context: ProjectContext, upstream: dict[str, SkillResult]) -> tuple[str, str | None]:
        """
        Construct the full prompt.
        Returns: tuple of (user_prompt, system_prompt)
        """
        pass

    @abstractmethod
    def parse_response(self, raw: str) -> BaseModel:
        """Parse and validate AI response into the output schema."""
        pass

    def validate_context(self, context: ProjectContext) -> None:
        """
        Validates that required context fields are present.
        Can be overridden by subclasses for tighter constraints.
        """
        pass

    def execute(self, context: ProjectContext, upstream: dict[str, SkillResult], ai_provider: AIProvider) -> SkillResult:
        """Main entry point. Template method implementing the lifecycle."""
        # 1. Validate
        self.validate_context(context)
        
        # 2. Build Prompt
        user_prompt, system_prompt = self.build_prompt(context, upstream)
        
        # 3. Execute with retries (for parsing errors)
        max_attempts = 2
        last_error = None
        
        start_time = time.time()
        
        for attempt in range(max_attempts):
            try:
                # If retrying due to schema error, append the error to the prompt
                prompt_to_send = user_prompt
                if attempt > 0 and last_error:
                    prompt_to_send += f"\n\nERROR IN PREVIOUS ATTEMPT:\n{str(last_error)}\nPlease fix the JSON."
                
                ai_response = ai_provider.generate(
                    prompt=prompt_to_send,
                    system_prompt=system_prompt
                )
                
                # 4. Parse & Validate
                parsed_output = self.parse_response(ai_response.text)
                
                duration = time.time() - start_time
                
                # 5. Return typed SkillResult
                return SkillResult(
                    skill_name=self.name,
                    skill_version=self.version,
                    output=parsed_output,
                    model_used=ai_response.model,
                    prompt_tokens=ai_response.prompt_tokens,
                    completion_tokens=ai_response.completion_tokens,
                    duration_seconds=duration,
                    raw_response=ai_response.text
                )
            except SkillOutputValidationError as e:
                last_error = e
                if attempt == max_attempts - 1:
                    raise
        
        raise SkillOutputValidationError(f"Failed to generate valid output after {max_attempts} attempts. Last error: {last_error}")
