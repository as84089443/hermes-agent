from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.case_repository import CaseRepository
from agent_workflow.intake_service import IntakeService
from agent_workflow.routing_engine import RoutingEngine
from agent_workflow.sidecar_resolver import SidecarResolver
from agent_workflow.storage import WorkflowStorage


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_service(tmp_path: Path) -> IntakeService:
    exports = tmp_path / "exports"
    exports.mkdir()
    _write_json(
        exports / "vendor_master_sidecar_v1.json",
        [
            {
                "名稱": "碼非創意企業有限公司",
                "匯款接洽人": "Ken\nJeffrey",
                "client_owner_guess": "我",
                "pm_owner_guess": "我",
                "relationship_type_guess": "我的直接客戶",
                "confidence": "high",
                "notes": "",
            }
        ],
    )
    _write_json(
        exports / "customer_brand_sidecar_v1.json",
        [
            {
                "name": "麻花影像",
                "owner_type_guess": "共同",
                "pm_owner_guess": "共同",
                "operating_note": "婚禮共同品牌",
                "confidence": "high",
                "aliases": ["麻花"],
            }
        ],
    )
    _write_json(
        exports / "analysis_rulebook_v1.json",
        {
            "do_not_ask_client_again": ["小白故事線上課程拍攝-台南"],
            "confirmed_client_lines": {
                "永恆少年行銷": "Brian direct client line"
            },
        },
    )
    resolver = SidecarResolver(exports_dir=exports)
    routing = RoutingEngine(resolver)
    storage = WorkflowStorage(tmp_path / "workflow_cases.db")
    repo = CaseRepository(storage)
    return IntakeService(repository=repo, routing_engine=routing)



def test_intake_service_builds_case_draft(tmp_path: Path):
    service = _make_service(tmp_path)
    draft = service.build_case_draft(
        title="碼非直播-操機",
        source="telegram",
        customer_name="碼非創意企業有限公司",
        raw_brief="企業活動直播拍攝，Brian 會下場",
    )

    assert draft["primary_lane"] == "commercial"
    assert draft["client_owner"] == "我"
    assert draft["pm_owner"] == "我"
    assert draft["status"] == "ready_for_quote"
    assert draft["routing_result"]["confidence"] == "high"
    service.close()



def test_intake_service_creates_case_from_intake(tmp_path: Path):
    service = _make_service(tmp_path)
    case = service.create_case_from_intake(
        title="麻花婚禮午宴",
        source="telegram",
        raw_brief="婚禮平面與動態",
    )

    assert case["case_id"].startswith("case_")
    assert case["primary_lane"] == "wedding_private"
    assert case["client_owner"] == "共同"
    assert case["pm_owner"] == "共同"
    service.close()



def test_intake_service_keeps_unknown_case_in_clarifying(tmp_path: Path):
    service = _make_service(tmp_path)
    case = service.create_case_from_intake(
        title="完全未知新案",
        source="telegram",
        raw_brief="需要拍攝一場活動，但客戶還不確定",
    )

    assert case["status"] == "clarifying"
    assert "missing_key_fields" in case["risk_flags"]
    service.close()
