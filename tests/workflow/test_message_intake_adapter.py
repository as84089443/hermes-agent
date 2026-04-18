from __future__ import annotations

from agent_workflow.message_intake_adapter import MessageIntakeAdapter
from agent_workflow.workflow_service import WorkflowService
from agent_workflow.case_repository import CaseRepository
from agent_workflow.routing_engine import RoutingEngine
from agent_workflow.sidecar_resolver import SidecarResolver
from agent_workflow.storage import WorkflowStorage

import json
from pathlib import Path


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def test_message_intake_adapter_parses_structured_message():
    adapter = MessageIntakeAdapter()
    result = adapter.parse(
        "客戶：碼非創意企業有限公司\n案名：碼非直播-操機\n類型：企業活動拍攝\n日期/交期：10/07\nBrian出工：是\n補充：Jerry 一起，Chu 後製"
    )

    assert result["title"] == "碼非直播-操機"
    assert result["customer_name"] == "碼非創意企業有限公司"
    assert result["metadata"]["job_type"] == "企業活動拍攝"
    assert result["metadata"]["brian_exec_hint"] == "是"



def test_message_intake_adapter_falls_back_to_first_line():
    adapter = MessageIntakeAdapter()
    result = adapter.parse("這是新案\n需要拍攝一場活動，但客戶還不確定")

    assert result["title"] == "這是新案"
    assert "原始訊息：" in result["raw_brief"]



def _make_workflow_service(tmp_path: Path) -> WorkflowService:
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
    _write_json(exports / "customer_brand_sidecar_v1.json", [])
    _write_json(exports / "analysis_rulebook_v1.json", {"do_not_ask_client_again": [], "confirmed_client_lines": {}})
    resolver = SidecarResolver(exports_dir=exports)
    routing = RoutingEngine(resolver)
    storage = WorkflowStorage(tmp_path / "workflow_cases.db")
    repo = CaseRepository(storage)
    return WorkflowService(repository=repo, resolver=resolver, routing_engine=routing)



def test_workflow_service_intake_message_creates_case(tmp_path: Path):
    service = _make_workflow_service(tmp_path)
    result = service.intake_message(
        message="客戶：碼非創意企業有限公司\n案名：碼非直播-操機\n類型：企業活動拍攝\nBrian出工：是",
        draft_only=False,
    )

    parsed = result["parsed_message"]
    workflow_result = result["workflow_result"]
    assert parsed["title"] == "碼非直播-操機"
    assert workflow_result["case"]["customer_name"] == "碼非創意企業有限公司"
    assert workflow_result["case"]["status"] == "ready_for_quote"
    service.close()
