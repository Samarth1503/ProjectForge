import pytest
from projectforge.config import Settings

def test_settings_defaults(monkeypatch):
    """Test that settings load correctly with defaults when no env variables are set."""
    # Ensure no environment variables leak into the test
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("PROJECTFORGE_MODEL", raising=False)
    
    settings = Settings()
    
    assert settings.projectforge_model == "gemini-2.5-flash"
    assert settings.projectforge_temperature == 0.2
    assert settings.projectforge_max_retries == 3
    
    with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
        settings.validate_api_key()

def test_settings_custom(monkeypatch):
    """Test that settings load correctly from environment variables."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
    monkeypatch.setenv("PROJECTFORGE_MODEL", "gemini-2.5-pro")
    
    settings = Settings()
    
    assert settings.gemini_api_key.get_secret_value() == "test_key_123"
    assert settings.projectforge_model == "gemini-2.5-pro"
    
    # Should not raise
    settings.validate_api_key()
