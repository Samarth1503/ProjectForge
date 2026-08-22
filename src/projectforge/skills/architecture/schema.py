from pydantic import BaseModel, Field

class Component(BaseModel):
    name: str
    type: str
    description: str
    technology: str
    responsibilities: list[str] = Field(min_length=1)

class DataFlowEdge(BaseModel):
    source: str
    target: str
    description: str
    protocol: str

class ArchitectureOutput(BaseModel):
    architecture_pattern: str
    pattern_rationale: str
    components: list[Component] = Field(min_length=2)
    data_flow: list[DataFlowEdge] = Field(min_length=1)
    technology_stack: dict[str, str]
    deployment_strategy: str
    deployment_rationale: str
    directory_structure: list[str]
    scalability_notes: str
    security_considerations: list[str] = Field(min_length=1)
