from typing import Type
from collections import defaultdict, deque

from projectforge.skills.base import BaseSkill
from projectforge.errors import SkillNotFoundError, SkillRegistryError, SkillDependencyError

class SkillRegistry:
    """Static registry for managing and discovering skills."""
    
    _skills: dict[str, Type[BaseSkill]] = {}

    @classmethod
    def register(cls, skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
        """Decorator to register a skill class."""
        # Need to instantiate temporarily to get properties if they are instance properties,
        # but in Python @property on a class requires an instance.
        # Actually, let's instantiate the skill to register it, or we expect skills to be instantiated when needed.
        # Let's instantiate a dummy to read metadata.
        try:
            instance = skill_class()
            name = instance.name
        except Exception as e:
            raise SkillRegistryError(f"Failed to instantiate {skill_class.__name__} for registration: {e}")

        if name in cls._skills:
            raise SkillRegistryError(f"A skill named '{name}' is already registered.")
        
        cls._skills[name] = skill_class
        return skill_class

    @classmethod
    def get_skill(cls, name: str) -> Type[BaseSkill]:
        """Retrieve a skill class by name."""
        if name not in cls._skills:
            raise SkillNotFoundError(f"Skill '{name}' not found.")
        return cls._skills[name]

    @classmethod
    def list_skills(cls) -> list[dict]:
        """List metadata for all registered skills."""
        metadata_list = []
        for name, skill_class in cls._skills.items():
            instance = skill_class()
            metadata_list.append({
                "name": instance.name,
                "display_name": instance.display_name,
                "description": instance.description,
                "version": instance.version,
                "depends_on": instance.depends_on,
            })
        return metadata_list

    @classmethod
    def get_execution_order(cls, requested: list[str]) -> list[str]:
        """
        Return a topological sort of the requested skills and their dependencies.
        If 'all' is in requested, it resolves all registered skills.
        """
        if "all" in requested:
            requested = list(cls._skills.keys())

        # Build graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Helper to recursively add dependencies
        def add_to_graph(skill_name):
            if skill_name not in cls._skills:
                raise SkillNotFoundError(f"Dependency skill '{skill_name}' not found in registry.")
            if skill_name not in in_degree:
                in_degree[skill_name] = 0
                instance = cls._skills[skill_name]()
                for dep in instance.depends_on:
                    graph[dep].append(skill_name)
                    in_degree[skill_name] += 1
                    add_to_graph(dep)

        for req in requested:
            add_to_graph(req)

        # Kahn's algorithm
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        ordered = []
        
        while queue:
            node = queue.popleft()
            ordered.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(ordered) != len(in_degree):
            raise SkillDependencyError("Circular dependency detected among skills.")
            
        return ordered

    @classmethod
    def clear(cls):
        """Clear registry (mostly for testing)."""
        cls._skills.clear()

def register_skill(skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
    """Decorator alias for SkillRegistry.register."""
    return SkillRegistry.register(skill_class)
