import importlib.util
import sys
from pathlib import Path


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "project_writeback_live_smoke.py"
    spec = importlib.util.spec_from_file_location("project_writeback_live_smoke_test", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_smoke_check_executes_review_verify_escalate_and_validates_detail(monkeypatch):
    mod = load_module()
    calls = []

    def fake_request_json(method, url, payload=None):
        calls.append((method, url, payload))
        if method == "POST" and url.endswith("/api/projects"):
            return {
                "id": "proj_test",
                "title": "Phase4 Writeback Live Check",
            }
        if method == "POST" and url.endswith("/api/projects/proj_test/pause"):
            return {"ok": True, "project": {"id": "proj_test", "autopilot_enabled": False}}
        if method == "POST" and url.endswith("/api/projects/proj_test/review"):
            return {"ok": True, "task": {"id": "task_1", "status": "review_passed"}}
        if method == "POST" and url.endswith("/api/projects/proj_test/verify"):
            return {
                "ok": True,
                "artifact": {"id": "artifact_1", "artifact_type": "verification-report"},
            }
        if method == "POST" and url.endswith("/api/projects/proj_test/escalate"):
            return {"ok": True, "project": {"id": "proj_test", "status": "blocked"}}
        if method == "GET" and url.endswith("/api/projects/proj_test"):
            return {
                "id": "proj_test",
                "status": "blocked",
                "waiting_reason": "escalate live check",
                "tasks": [
                    {
                        "id": "task_1",
                        "status": "blocked",
                        "blocking_reason": "escalate live check",
                        "output_artifact_id": "artifact_1",
                    }
                ],
                "recent_events": [
                    {"event_type": "escalation_raised"},
                    {"event_type": "verification_recorded"},
                    {"event_type": "artifact_written"},
                    {"event_type": "review_decided"},
                ],
            }
        raise AssertionError(f"Unexpected call: {(method, url, payload)!r}")

    monkeypatch.setattr(mod, "request_json", fake_request_json)

    result = mod.run_smoke_check(
        base_url="http://127.0.0.1:9119",
        title="Phase4 Writeback Live Check",
        phase_goal="驗證 review / verify / escalation writeback live 生效",
        next_action_summary="先跑 review、verify、escalate 三段回寫，確認 live project detail 有反映。",
        review_notes="spec 與品質都過",
        verify_summary="手動驗證通過",
        escalation_reason="escalate live check",
        pause_autopilot=True,
    )

    assert result["ok"] is True
    assert result["project_id"] == "proj_test"
    assert result["review_task_status"] == "review_passed"
    assert result["verify_artifact_type"] == "verification-report"
    assert result["final_project_status"] == "blocked"
    assert result["latest_task_status"] == "blocked"
    assert result["latest_task_output_artifact_id"] == "artifact_1"
    assert result["recent_event_types"][:4] == [
        "escalation_raised",
        "verification_recorded",
        "artifact_written",
        "review_decided",
    ]
    assert [method for method, _, _ in calls] == ["POST", "POST", "POST", "POST", "POST", "GET"]
