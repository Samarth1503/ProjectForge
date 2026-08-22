import pytest
from pydantic import ValidationError
from projectforge.models import ProjectContext, ProjectType, AcademicLevel, SkillResult
from pydantic import BaseModel

class DummyOutput(BaseModel):
    message: str

def test_project_context_valid():
    ctx = ProjectContext(
        project_title="Test Project",
        project_description="This is a test project that is long enough to pass validation.",
        project_type=ProjectType.web_app
    )
    assert ctx.project_title == "Test Project"
    assert ctx.team_size == 1
    assert ctx.academic_level == AcademicLevel.undergrad

def test_project_context_invalid_title():
    with pytest.raises(ValidationError):
        ProjectContext(
            project_title="A", # Too short
            project_description="This is a test project that is long enough to pass validation.",
            project_type=ProjectType.web_app
        )

def test_project_context_invalid_description():
    with pytest.raises(ValidationError):
        ProjectContext(
            project_title="Test Project",
            project_description="Too short",
            project_type=ProjectType.web_app
        )

def test_skill_result():
    out = DummyOutput(message="Hello")
    result = SkillResult(
        skill_name="test_skill",
        skill_version="1.0.0",
        output=out,
        model_used="test-model",
        duration_seconds=1.5,
        raw_response='{"message": "Hello"}'
    )
    assert result.skill_name == "test_skill"
    assert result.output.message == "Hello"
