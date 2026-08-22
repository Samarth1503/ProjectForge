import pytest
from projectforge.models import ProjectContext, ProjectType
from projectforge.skills.requirements.skill import RequirementsSkill
from tests.fakes import FakeAIProvider
from projectforge.errors import SkillOutputValidationError

import json

VALID_RESPONSE = {
    "project_summary": "Test Summary",
    "functional_requirements": [
        {"id": "FR-1", "title": "T1", "description": "D1", "priority": "must_have", "category": "Core"},
        {"id": "FR-2", "title": "T2", "description": "D2", "priority": "should_have", "category": "Core"},
        {"id": "FR-3", "title": "T3", "description": "D3", "priority": "could_have", "category": "Core"}
    ],
    "non_functional_requirements": [
        {"id": "NFR-1", "title": "N1", "description": "D1", "category": "Perf"},
        {"id": "NFR-2", "title": "N2", "description": "D2", "category": "Sec"}
    ],
    "user_stories": [
        {"id": "US-1", "role": "User", "action": "do", "benefit": "get", "priority": "must_have", "acceptance_criteria": ["Crit1"]},
        {"id": "US-2", "role": "User", "action": "do", "benefit": "get", "priority": "must_have", "acceptance_criteria": ["Crit1"]},
        {"id": "US-3", "role": "User", "action": "do", "benefit": "get", "priority": "must_have", "acceptance_criteria": ["Crit1"]}
    ],
    "scope_in": ["Thing 1"],
    "scope_out": ["Thing 2"],
    "assumptions": ["Assump 1"],
    "risks": ["Risk 1"]
}

def test_requirements_skill_success():
    skill = RequirementsSkill()
    ctx = ProjectContext(
        project_title="Test Project",
        project_description="A test project with at least 20 chars.",
        project_type=ProjectType.web_app
    )
    
    provider = FakeAIProvider([json.dumps(VALID_RESPONSE)])
    result = skill.execute(ctx, {}, provider)
    
    assert result.skill_name == "requirements"
    assert len(result.output.functional_requirements) == 3
    assert len(result.output.user_stories) == 3
    assert result.output.project_summary == "Test Summary"

def test_requirements_skill_missing_fields():
    skill = RequirementsSkill()
    ctx = ProjectContext(
        project_title="Test Project",
        project_description="A test project with at least 20 chars.",
        project_type=ProjectType.web_app
    )
    
    invalid_resp = dict(VALID_RESPONSE)
    del invalid_resp["functional_requirements"]
    
    # Needs two errors because of retry
    provider = FakeAIProvider([json.dumps(invalid_resp), json.dumps(invalid_resp)])
    
    with pytest.raises(SkillOutputValidationError, match="functional_requirements"):
        skill.execute(ctx, {}, provider)
