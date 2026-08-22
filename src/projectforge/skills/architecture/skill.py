import os
from pydantic import BaseModel, ValidationError

from projectforge.skills.base import BaseSkill
from projectforge.skills.registry import register_skill
from projectforge.models import ProjectContext, SkillResult
from projectforge.utils import extract_json_from_text
from projectforge.errors import SkillOutputValidationError, SkillDependencyError
from .schema import ArchitectureOutput

@register_skill
class ArchitectureSkill(BaseSkill):
    @property
    def name(self) -> str: return "architecture"
    @property
    def display_name(self) -> str: return "Architecture Design"
    @property
    def description(self) -> str: return "Produces a system architecture recommendation."
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def depends_on(self) -> list[str]: return ["requirements"]

    def get_output_schema(self) -> type[BaseModel]:
        return ArchitectureOutput

    def build_prompt(self, context: ProjectContext, upstream: dict[str, SkillResult]) -> tuple[str, str | None]:
        if "requirements" not in upstream:
            raise SkillDependencyError("Architecture skill requires 'requirements' output.")
            
        reqs = upstream["requirements"].output.model_dump_json(indent=2)
        
        system_prompt = f"You are a Software Architect.\nRespond ONLY with JSON.\n{ArchitectureOutput.model_json_schema()}"
        
        user_prompt = f"""
## Project
Title: {context.project_title}
Type: {context.project_type.value}
Tech Preferences: {context.tech_preferences}

## Requirements
{reqs}
"""
        return user_prompt, system_prompt

    def parse_response(self, raw: str) -> BaseModel:
        try:
            parsed_json = extract_json_from_text(raw)
            out = ArchitectureOutput(**parsed_json)
            # Cross-reference validation
            comp_names = {c.name for c in out.components}
            for edge in out.data_flow:
                if edge.source not in comp_names or edge.target not in comp_names:
                    raise SkillOutputValidationError(f"Data flow references unknown components: {edge.source}->{edge.target}")
            return out
        except (ValueError, ValidationError) as e:
            raise SkillOutputValidationError(str(e))
