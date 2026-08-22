import os
from pydantic import BaseModel, ValidationError

from projectforge.skills.base import BaseSkill
from projectforge.skills.registry import register_skill
from projectforge.models import ProjectContext, SkillResult
from projectforge.utils import extract_json_from_text
from projectforge.errors import SkillOutputValidationError, SkillDependencyError
from .schema import DatabaseOutput

@register_skill
class DatabaseSkill(BaseSkill):
    @property
    def name(self) -> str: return "database"
    @property
    def display_name(self) -> str: return "Database Design"
    @property
    def description(self) -> str: return "Produces a database schema design."
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def depends_on(self) -> list[str]: return ["requirements", "architecture"]

    def get_output_schema(self) -> type[BaseModel]:
        return DatabaseOutput

    def build_prompt(self, context: ProjectContext, upstream: dict[str, SkillResult]) -> tuple[str, str | None]:
        if "requirements" not in upstream or "architecture" not in upstream:
            raise SkillDependencyError("Database skill requires 'requirements' and 'architecture' outputs.")
            
        system_prompt = f"You are a Database Engineer.\nRespond ONLY with JSON.\n{DatabaseOutput.model_json_schema()}"
        user_prompt = f"Design a database for:\n{upstream['requirements'].output.model_dump_json()}\nArch:\n{upstream['architecture'].output.model_dump_json()}"
        return user_prompt, system_prompt

    def parse_response(self, raw: str) -> BaseModel:
        try:
            parsed_json = extract_json_from_text(raw)
            return DatabaseOutput(**parsed_json)
        except (ValueError, ValidationError) as e:
            raise SkillOutputValidationError(str(e))
