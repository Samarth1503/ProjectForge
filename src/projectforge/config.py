from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables and .env file."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: SecretStr = Field(default=SecretStr(""))
    projectforge_model: str = "gemini-2.5-flash"
    projectforge_temperature: float = 0.2
    projectforge_max_output_tokens: int = 8192
    projectforge_request_timeout: int = 120
    projectforge_max_retries: int = 3
    projectforge_log_level: str = "INFO"
    projectforge_output_dir: str = ".projectforge/outputs"

    def validate_api_key(self) -> None:
        """Validates that the API key is present."""
        if not self.gemini_api_key.get_secret_value():
            raise ValueError("GEMINI_API_KEY is missing or empty. Please set it in .env")

# Global singleton
settings = Settings()
