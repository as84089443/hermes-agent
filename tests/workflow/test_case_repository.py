from __future__ import annotations

from pathlib import Path

import pytest

from agent_workflow.case_repository import CaseRepository
from agent_workflow.case_validation import CaseValidationError
from agent_workflow.storage import WorkflowStorage


@pytest.fixture
def repo(tmp_path: Path) -> CaseRepository:
    storage = WorkflowStorage(tmp_path / "workflow_cases.db")
    repository = CaseRepository(storage)
    yield repository
    repository.close()


def _create_case(repo: CaseRepository, **overrides):
    payload = {
        "title": "Test case",
        "source": "manual",
        "customer_name": "Test Customer",
        "primary_lane": "commercial",
        "current_owner": "Brian",
        "next_action": "Clarify scope",
        "next_owner": "Brian",
        "raw_brief": "Need a commercial shoot",
    }
    payload.update(overrides)
    return repo.create_case(**payload)


def test_create_case_success(repo: CaseRepository):
    case = _create_case(repo)
    assert case["case_id"].startswith("case_")
    assert case["status"] == "intake"
    assert case["primary_lane"] == "commercial"


def test_create_case_missing_required_field_fails(repo: CaseRepository):
    with pytest.raises(CaseValidationError):
        repo.create_case(
            title="Bad case",
            source="manual",
            customer_name="",
            primary_lane="commercial",
            current_owner="Brian",
            next_action="Clarify scope",
            next_owner="Brian",
        )


def test_invalid_enum_fails(repo: CaseRepository):
    with pytest.raises(CaseValidationError):
        _create_case(repo, primary_lane="not-a-lane")


def test_get_case_returns_record(repo: CaseRepository):
    created = _create_case(repo)
    fetched = repo.get_case(created["case_id"])
    assert fetched is not None
    assert fetched["case_id"] == created["case_id"]


def test_list_cases_filters_by_status(repo: CaseRepository):
    first = _create_case(repo)
    repo.transition_case(first["case_id"], "clarifying")
    _create_case(repo, title="Second case")
    clarifying = repo.list_cases(status="clarifying")
    assert len(clarifying) == 1
    assert clarifying[0]["status"] == "clarifying"


def test_update_allowed_field(repo: CaseRepository):
    created = _create_case(repo)
    updated = repo.update_case_fields(created["case_id"], {"client_owner": "我", "notes": "updated"})
    assert updated["client_owner"] == "我"
    assert updated["notes"] == "updated"


def test_update_status_directly_fails(repo: CaseRepository):
    created = _create_case(repo)
    with pytest.raises(CaseValidationError):
        repo.update_case_fields(created["case_id"], {"status": "clarifying"})


def test_legal_transition_success(repo: CaseRepository):
    created = _create_case(repo)
    transitioned = repo.transition_case(created["case_id"], "clarifying")
    assert transitioned["status"] == "clarifying"


def test_illegal_transition_fails(repo: CaseRepository):
    created = _create_case(repo)
    with pytest.raises(CaseValidationError):
        repo.transition_case(created["case_id"], "closed")


def test_confirmed_transition_sets_scope_lock(repo: CaseRepository):
    created = _create_case(repo)
    repo.transition_case(created["case_id"], "ready_for_quote")
    confirmed = repo.transition_case(created["case_id"], "confirmed")
    assert confirmed["status"] == "confirmed"
    assert confirmed["scope_locked_at"] is not None
