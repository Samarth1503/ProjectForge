import pytest
from pydantic import BaseModel
from projectforge.skills.base import BaseSkill
from projectforge.models import ProjectContext, ProjectType, SkillResult
from projectforge.ai.provider import AIProvider, AIResponse
from projectforge.errors import SkillOutputValidationError

class DummySchema(BaseModel):
    message: str

class DummySkill(BaseSkill):
    @property
    def name(self) -> str: return "dummy"
    @property
    def display_name(self) -> str: return "Dummy Skill"
    @property
    def description(self) -> str: return "A test skill"
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def depends_on(self) -> list[str]: return []

    def get_output_schema(self):
        return DummySchema

    def build_prompt(self, context, upstream):
        return "Say hello", "You are an assistant"

    def parse_response(self, raw: str):
        if "error" in raw:
            raise SkillOutputValidationError("Simulated parsing error")
        return DummySchema(message="Parsed correctly")

class FakeProvider:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def generate(self, prompt, system_prompt=None, **kwargs):
        resp = self.responses[self.call_count]
        self.call_count += 1
        return AIResponse(text=resp, model="fake-model")

def test_base_skill_success():
    skill = DummySkill()
    ctx = ProjectContext(project_title="Test", project_description="D"*20, project_type=ProjectType.other)
    
    provider = FakeProvider(["OK"])
    result = skill.execute(ctx, {}, provider)
    
    assert result.skill_name == "dummy"
    assert result.output.message == "Parsed correctly"
    assert result.model_used == "fake-model"
    assert provider.call_count == 1

def test_base_skill_retry_success():
    skill = DummySkill()
    ctx = ProjectContext(project_title="Test", project_description="D"*20, project_type=ProjectType.other)
    
    # First response causes parsing error, second succeeds
    provider = FakeProvider(["error response", "OK"])
    result = skill.execute(ctx, {}, provider)
    
    assert result.output.message == "Parsed correctly"
    assert provider.call_count == 2

def test_base_skill_retry_failure():
    skill = DummySkill()
    ctx = ProjectContext(project_title="Test", project_description="D"*20, project_type=ProjectType.other)
    
    # Both responses cause parsing errors
    provider = FakeProvider(["error 1", "error 2"])
    
    with pytest.raises(SkillOutputValidationError, match="Simulated parsing error"):
        skill.execute(ctx, {}, provider)
    
    assert provider.call_count == 2
