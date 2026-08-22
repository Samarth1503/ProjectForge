# Import all skills so they register themselves when this package is imported
from .registry import SkillRegistry, register_skill
from .base import BaseSkill

# Explicitly import all skill modules
from .requirements import skill as _requirements
from .architecture import skill as _architecture
from .database import skill as _database
from .api import skill as _api
from .project_plan import skill as _project_plan

__all__ = ["SkillRegistry", "register_skill", "BaseSkill"]
