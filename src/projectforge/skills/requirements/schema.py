from pydantic import BaseModel, Field
from projectforge.models import Priority

class UserStory(BaseModel):
    id: str
    role: str
    action: str
    benefit: str
    priority: Priority
    acceptance_criteria: list[str] = Field(min_length=1)

class FunctionalRequirement(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority
    category: str

class NonFunctionalRequirement(BaseModel):
    id: str
    title: str
    description: str
    category: str

class RequirementsOutput(BaseModel):
    project_summary: str
    functional_requirements: list[FunctionalRequirement] = Field(min_length=3)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(min_length=2)
    user_stories: list[UserStory] = Field(min_length=3)
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[str] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
