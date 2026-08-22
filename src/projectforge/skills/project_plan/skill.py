import os
from pydantic import BaseModel, ValidationError

from projectforge.skills.base import BaseSkill
from projectforge.skills.registry import register_skill
from projectforge.models import ProjectContext, SkillResult
from projectforge.utils import extract_json_from_text
from projectforge.errors import SkillOutputValidationError, SkillDependencyError
from .schema import ProjectPlanOutput

@register_skill
class ProjectPlanSkill(BaseSkill):
    @property
    def name(self) -> str: return "project_plan"
    @property
    def display_name(self) -> str: return "Project Plan"
    @property
    def description(self) -> str: return "Produces an implementation plan."
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def depends_on(self) -> list[str]: return ["requirements", "architecture", "database", "api"]

    def get_output_schema(self) -> type[BaseModel]:
        return ProjectPlanOutput

    def build_prompt(self, context: ProjectContext, upstream: dict[str, SkillResult]) -> tuple[str, str | None]:
        for dep in self.depends_on:
            if dep not in upstream:
                raise SkillDependencyError(f"Project plan requires '{dep}' output.")
            
        system_prompt = f"You are a Project Manager.\nRespond ONLY with JSON.\n{ProjectPlanOutput.model_json_schema()}"
        user_prompt = f"Design a plan for this project:\nReqs: {upstream['requirements'].output.model_dump_json()}\nArch: {upstream['architecture'].output.model_dump_json()}\nDB: {upstream['database'].output.model_dump_json()}\nAPI: {upstream['api'].output.model_dump_json()}"
        return user_prompt, system_prompt

    def parse_response(self, raw: str) -> BaseModel:
        try:
            parsed_json = extract_json_from_text(raw)
            return ProjectPlanOutput(**parsed_json)
        except (ValueError, ValidationError) as e:
            raise SkillOutputValidationError(str(e))
