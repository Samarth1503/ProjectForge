from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ProjectType(str, Enum):
    web_app = "web_app"
    mobile_app = "mobile_app"
    desktop_app = "desktop_app"
    api_service = "api_service"
    cli_tool = "cli_tool"
    library = "library"
    data_pipeline = "data_pipeline"
    ml_project = "ml_project"
    iot_system = "iot_system"
    other = "other"

class AcademicLevel(str, Enum):
    undergrad = "undergrad"
    postgrad = "postgrad"
    phd = "phd"

class Priority(str, Enum):
    must_have = "must_have"
    should_have = "should_have"
    could_have = "could_have"
    wont_have = "wont_have"

class ProjectContext(BaseModel):
    """Immutable project information gathered from the user."""
    project_title: str = Field(..., min_length=3)
    project_description: str = Field(..., min_length=20, max_length=5000)
    project_type: ProjectType
    tech_preferences: list[str] = Field(default_factory=list)
    target_users: str = ""
    constraints: list[str] = Field(default_factory=list)
    team_size: int = Field(default=1, ge=1, le=10)
    timeline_weeks: Optional[int] = None
    academic_level: AcademicLevel = AcademicLevel.undergrad
    additional_notes: str = Field(default="", max_length=2000)

def get_utc_now(): return datetime.now(timezone.utc)

class SkillResult(BaseModel):
    skill_name: str
    skill_version: str
    output: BaseModel
    timestamp: datetime = Field(default_factory=get_utc_now)
    model_used: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    duration_seconds: float
    raw_response: str
