from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.routing_engine import RoutingEngine
from agent_workflow.routing_mismatch_tracker import RoutingMismatchTracker
from agent_workflow.sidecar_resolver import SidecarResolver


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_engine(tmp_path: Path) -> RoutingEngine:
    exports = tmp_path / "exports"
    exports.mkdir()
    _write_json(
        exports / "vendor_master_sidecar_v1.json",
        [
            {
                "名稱": "永恆少年行銷",
                "匯款接洽人": "哈利",
                "client_owner_guess": "我",
                "pm_owner_guess": "我",
                "relationship_type_guess": "我的直接客戶",
                "confidence": "high",
                "notes": "",
            }
        ],
    )
    _write_json(exports / "customer_brand_sidecar_v1.json", [])
    _write_json(
        exports / "analysis_rulebook_v1.json",
        {
            "do_not_ask_client_again": [],
            "confirmed_client_lines": {
                "永恆少年行銷": "Brian direct client line"
            },
        },
    )
    resolver = SidecarResolver(exports_dir=exports)
    return RoutingEngine(resolver)



def test_routing_mismatch_tracker_detects_execution_role_mismatch(tmp_path: Path):
    engine = _make_engine(tmp_path)
    tracker = RoutingMismatchTracker()
    case = {
        "case_id": "case_1",
        "title": "Brian單機-哈利_跑跑薑餅人",
        "raw_brief": "永恆少年行銷案源，商業拍攝案件",
        "customer_name": "永恆少年行銷",
        "brand_or_system": "Brian direct",
        "source": "telegram",
        "primary_lane": "commercial",
        "status": "clarifying",
    }
    routing = engine.route(title=case["title"], customer_name=case["customer_name"], raw_brief=case["raw_brief"])
    final_values = {
        "primary_lane": "commercial",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "否",
        "brian_role": "僅管理",
        "created_by": "Brian",
    }
    mismatch = tracker.build_mismatch(case=case, routing_result=routing, final_values=final_values, human_explanation="這案是我接案後外發")

    assert "brian_exec" in mismatch["mismatched_fields"]
    assert "brian_role" in mismatch["mismatched_fields"]
    assert mismatch["mismatch_type"] == "multi_factor"
    assert mismatch["routing_prompt_eval_candidate"] is True



def test_routing_mismatch_tracker_detects_customer_ownership_mismatch(tmp_path: Path):
    engine = _make_engine(tmp_path)
    tracker = RoutingMismatchTracker()
    case = {
        "case_id": "case_2",
        "title": "某共同客戶直播",
        "raw_brief": "收入接近，應該是共同客戶",
        "customer_name": "陌生客戶",
        "source": "telegram",
        "primary_lane": "commercial",
        "status": "clarifying",
    }
    routing = engine.route(title=case["title"], customer_name=case["customer_name"], raw_brief=case["raw_brief"])
    final_values = {
        "primary_lane": "commercial",
        "client_owner": "共同",
        "pm_owner": "共同",
        "brian_exec": "是",
        "brian_role": "主輸出",
    }
    mismatch = tracker.build_mismatch(case=case, routing_result=routing, final_values=final_values, human_explanation="這是共同客戶線")

    assert mismatch["mismatch_type"] in {"customer_ownership_error", "multi_factor"}
    assert mismatch["customer_sidecar_update_needed"] is True



def test_routing_mismatch_tracker_no_mismatch_when_values_align(tmp_path: Path):
    engine = _make_engine(tmp_path)
    tracker = RoutingMismatchTracker()
    case = {
        "case_id": "case_3",
        "title": "一般商業拍攝",
        "raw_brief": "永恆少年行銷企業拍攝，我會親自拍",
        "customer_name": "永恆少年行銷",
        "source": "telegram",
        "primary_lane": "commercial",
        "status": "ready_for_quote",
    }
    routing = engine.route(title=case["title"], customer_name=case["customer_name"], raw_brief=case["raw_brief"])
    final_values = {
        "primary_lane": routing["primary_lane_candidate"],
        "client_owner": routing["client_owner_candidate"],
        "pm_owner": routing["pm_owner_candidate"],
        "brian_exec": routing["brian_exec_candidate"],
        "brian_role": routing["brian_role_candidate"],
    }
    mismatch = tracker.build_mismatch(case=case, routing_result=routing, final_values=final_values)

    assert mismatch["mismatched_fields"] == []
    assert mismatch["resolved"] is False
