from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str
    title: str
    description: str
    dependencies: list[str] = []
    estimated_hours: int
    assigned_role: str

class Milestone(BaseModel):
    id: str
    title: str
    description: str
    tasks: list[Task] = Field(min_length=1)

class Phase(BaseModel):
    name: str
    description: str
    milestones: list[Milestone] = Field(min_length=1)

class SetupInstructions(BaseModel):
    prerequisites: list[str]
    environment_variables: list[str]
    commands: list[str]
    ide_recommendations: list[str]

class ProjectPlanOutput(BaseModel):
    phases: list[Phase] = Field(min_length=1)
    setup_instructions: SetupInstructions
    testing_strategy: list[str]
    deployment_steps: list[str]
    recommended_git_workflow: str
