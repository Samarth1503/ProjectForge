import pytest
from pydantic import BaseModel
from projectforge.skills.base import BaseSkill
from projectforge.skills.registry import SkillRegistry, register_skill
from projectforge.errors import SkillNotFoundError, SkillRegistryError, SkillDependencyError

class DummySchema(BaseModel):
    pass

class A(BaseSkill):
    @property
    def name(self): return "a"
    @property
    def display_name(self): return "A"
    @property
    def description(self): return "A"
    @property
    def version(self): return "1"
    @property
    def depends_on(self): return []
    def get_output_schema(self): return DummySchema
    def build_prompt(self, ctx, up): return "", ""
    def parse_response(self, raw): return DummySchema()

class B(BaseSkill):
    @property
    def name(self): return "b"
    @property
    def display_name(self): return "B"
    @property
    def description(self): return "B"
    @property
    def version(self): return "1"
    @property
    def depends_on(self): return ["a"]
    def get_output_schema(self): return DummySchema
    def build_prompt(self, ctx, up): return "", ""
    def parse_response(self, raw): return DummySchema()

class C(BaseSkill):
    @property
    def name(self): return "c"
    @property
    def display_name(self): return "C"
    @property
    def description(self): return "C"
    @property
    def version(self): return "1"
    @property
    def depends_on(self): return ["b"]
    def get_output_schema(self): return DummySchema
    def build_prompt(self, ctx, up): return "", ""
    def parse_response(self, raw): return DummySchema()

@pytest.fixture(autouse=True)
def clean_registry():
    SkillRegistry.clear()
    yield
    SkillRegistry.clear()

def test_registry_registration():
    register_skill(A)
    assert SkillRegistry.get_skill("a") == A

    with pytest.raises(SkillRegistryError, match="already registered"):
        register_skill(A)

def test_registry_get_unknown():
    with pytest.raises(SkillNotFoundError):
        SkillRegistry.get_skill("unknown")

def test_registry_list_skills():
    register_skill(A)
    register_skill(B)
    
    skills = SkillRegistry.list_skills()
    assert len(skills) == 2
    assert skills[0]["name"] == "a"
    assert skills[1]["name"] == "b"

def test_registry_topological_sort():
    # Register out of order to ensure it sorts correctly
    register_skill(C)
    register_skill(A)
    register_skill(B)
    
    order = SkillRegistry.get_execution_order(["c"])
    assert order == ["a", "b", "c"]
    
    order_all = SkillRegistry.get_execution_order(["all"])
    # all should return a, b, c
    assert order_all == ["a", "b", "c"]
    
    order_b = SkillRegistry.get_execution_order(["b"])
    assert order_b == ["a", "b"]

def test_registry_missing_dependency():
    register_skill(B)
    # A is not registered
    with pytest.raises(SkillNotFoundError, match="Dependency skill 'a' not found"):
        SkillRegistry.get_execution_order(["b"])
