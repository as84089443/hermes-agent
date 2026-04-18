from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.case_repository import CaseRepository
from agent_workflow.routing_engine import RoutingEngine
from agent_workflow.sidecar_resolver import SidecarResolver
from agent_workflow.storage import WorkflowStorage
from agent_workflow.workflow_service import WorkflowService


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_service(tmp_path: Path) -> WorkflowService:
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
            },
            {
                "名稱": "永恆少年行銷",
                "匯款接洽人": "哈利",
                "client_owner_guess": "我",
                "pm_owner_guess": "我",
                "relationship_type_guess": "我的直接客戶",
                "confidence": "high",
                "notes": "",
            },
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
                "永恆少年行銷": "Brian direct client line",
                "碼非創意企業有限公司": "Brian direct client line"
            },
        },
    )
    resolver = SidecarResolver(exports_dir=exports)
    routing = RoutingEngine(resolver)
    storage = WorkflowStorage(tmp_path / "workflow_cases.db")
    repo = CaseRepository(storage)
    return WorkflowService(repository=repo, resolver=resolver, routing_engine=routing)



def test_workflow_service_intake_and_metrics(tmp_path: Path):
    service = _make_service(tmp_path)
    result = service.intake_case(
        title="碼非直播-操機",
        source="telegram",
        customer_name="碼非創意企業有限公司",
        raw_brief="企業活動直播拍攝，Brian 會下場",
    )

    assert result["case"]["status"] == "ready_for_quote"
    snapshot = service.get_metrics_snapshot()
    assert snapshot["routing_case_count"] == 1
    assert snapshot["routing_correction_rate"] == 0.0
    service.close()



def test_workflow_service_records_mismatch_and_updates_metrics(tmp_path: Path):
    service = _make_service(tmp_path)
    result = service.intake_case(
        title="Brian單機-哈利_跑跑薑餅人",
        source="telegram",
        customer_name="永恆少年行銷",
        raw_brief="商業拍攝案件",
    )
    case = result["case"]
    mismatch = service.record_routing_correction(
        case_id=case["case_id"],
        final_values={
            "primary_lane": "commercial",
            "client_owner": "我",
            "pm_owner": "我",
            "brian_exec": "否",
            "brian_role": "僅管理",
        },
        human_explanation="這案是我接案後外發",
    )

    assert mismatch["mismatched_fields"]
    snapshot = service.get_metrics_snapshot()
    assert snapshot["mismatch_count"] == 1
    assert snapshot["routing_correction_rate"] == 1.0
    service.close()



def test_workflow_service_close_case_with_recap(tmp_path: Path):
    service = _make_service(tmp_path)
    result = service.intake_case(
        title="碼非直播-操機",
        source="telegram",
        customer_name="碼非創意企業有限公司",
        raw_brief="企業活動直播拍攝，Brian 會下場",
    )
    case = result["case"]
    recap = service.close_case_with_recap(
        case_id=case["case_id"],
        recap_context={"created_by": "Brian", "brian_net": 20000},
    )

    assert recap["case_id"] == case["case_id"]
    assert recap["income_nature_final"] == "兼具PM與執行"
    snapshot = service.get_metrics_snapshot()
    assert snapshot["recap_count"] == 1
    service.close()
