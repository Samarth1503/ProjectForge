class ProjectForgeError(Exception):
    """Base exception for all ProjectForge errors."""
    pass

class ConfigurationError(ProjectForgeError):
    pass

class MissingAPIKeyError(ConfigurationError):
    pass

class InvalidConfigError(ConfigurationError):
    pass

class ProjectError(ProjectForgeError):
    pass

class ProjectNotInitializedError(ProjectError):
    pass

class InvalidProjectContextError(ProjectError):
    pass

class SkillError(ProjectForgeError):
    pass

class SkillNotFoundError(SkillError):
    pass

class SkillRegistryError(SkillError):
    pass

class SkillDependencyError(SkillError):
    pass

class SkillValidationError(SkillError):
    """Raised when the input context doesn't meet the skill's requirements."""
    pass

class SkillExecutionError(SkillError):
    """Raised on a general runtime failure inside a skill."""
    pass

class SkillOutputValidationError(SkillError):
    """Raised when the AI's response does not match the required schema."""
    pass

class AIProviderError(ProjectForgeError):
    pass

class AIProviderAuthError(AIProviderError):
    pass

class AIProviderRateLimitError(AIProviderError):
    pass

class AIProviderTimeoutError(AIProviderError):
    pass

class AIProviderSafetyError(AIProviderError):
    pass

class AIProviderEmptyResponseError(AIProviderError):
    pass

class AIProviderResponseError(AIProviderError):
    """Catch-all for other provider errors."""
    pass

class PromptError(ProjectForgeError):
    pass

class PromptTemplateError(PromptError):
    pass
