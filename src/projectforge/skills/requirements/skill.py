import os
from pydantic import BaseModel, ValidationError

from projectforge.skills.base import BaseSkill
from projectforge.skills.registry import register_skill
from projectforge.models import ProjectContext, SkillResult
from projectforge.utils import extract_json_from_text
from projectforge.errors import SkillOutputValidationError
from .schema import RequirementsOutput

@register_skill
class RequirementsSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "requirements"

    @property
    def display_name(self) -> str:
        return "Requirements Analysis"

    @property
    def description(self) -> str:
        return "Analyzes project ideas and produces structured requirements."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def depends_on(self) -> list[str]:
        return []

    def get_output_schema(self) -> type[BaseModel]:
        return RequirementsOutput

    def build_prompt(self, context: ProjectContext, upstream: dict[str, SkillResult]) -> tuple[str, str | None]:
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        
        with open(os.path.join(prompts_dir, "system.txt"), "r", encoding="utf-8") as f:
            system_template = f.read()
            
        with open(os.path.join(prompts_dir, "user.txt"), "r", encoding="utf-8") as f:
            user_template = f.read()

        # Generate JSON schema from Pydantic model
        schema_json = RequirementsOutput.model_json_schema()
        
        import json
        system_prompt = system_template.format(
            json_schema=json.dumps(schema_json, indent=2)
        )

        user_prompt = user_template.format(
            project_title=context.project_title,
            project_description=context.project_description,
            project_type=context.project_type.value,
            tech_preferences=", ".join(context.tech_preferences) if context.tech_preferences else "None",
            target_users=context.target_users or "General",
            constraints=", ".join(context.constraints) if context.constraints else "None",
            team_size=context.team_size,
            timeline_weeks=context.timeline_weeks or "Not specified",
            academic_level=context.academic_level.value,
            additional_notes=context.additional_notes or "None"
        )
        
        return user_prompt, system_prompt

    def parse_response(self, raw: str) -> BaseModel:
        try:
            parsed_json = extract_json_from_text(raw)
            return RequirementsOutput(**parsed_json)
        except ValueError as e:
            raise SkillOutputValidationError(f"Failed to extract JSON: {e}")
        except ValidationError as e:
            raise SkillOutputValidationError(f"JSON does not match schema: {e}")
