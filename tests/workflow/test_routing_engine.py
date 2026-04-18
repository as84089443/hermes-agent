from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.routing_engine import RoutingEngine
from agent_workflow.sidecar_resolver import SidecarResolver


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_resolver(tmp_path: Path) -> SidecarResolver:
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
                "永恆少年行銷": "Brian direct client line",
                "麻花影像 / VAF美式婚紗": "Shared wedding brand / shared client line",
            },
        },
    )
    return SidecarResolver(exports_dir=exports)


def test_routing_engine_routes_known_customer_to_ready_for_quote(tmp_path: Path):
    engine = RoutingEngine(_make_resolver(tmp_path))
    result = engine.route(title="碼非直播-操機", customer_name="碼非創意企業有限公司", raw_brief="企業活動直播拍攝")

    assert result["primary_lane_candidate"] == "commercial"
    assert result["client_owner_candidate"] == "我"
    assert result["pm_owner_candidate"] == "我"
    assert result["recommended_next_status"] == "ready_for_quote"
    assert result["confidence"] == "high"


def test_routing_engine_routes_wedding_brand(tmp_path: Path):
    engine = RoutingEngine(_make_resolver(tmp_path))
    result = engine.route(title="麻花婚禮午宴", raw_brief="婚禮平面與動態")

    assert result["primary_lane_candidate"] == "wedding_private"
    assert result["brand_or_system_candidate"] == "麻花影像"
    assert result["client_owner_candidate"] == "共同"
    assert result["pm_owner_candidate"] == "共同"


def test_routing_engine_detects_outsourced_pm_case(tmp_path: Path):
    engine = RoutingEngine(_make_resolver(tmp_path))
    result = engine.route(title="哈利_跑跑薑餅人", raw_brief="永恆少年行銷案源，我接案後外發給哈利拍攝")

    assert result["client_owner_candidate"] == "我"
    assert result["pm_owner_candidate"] == "我"
    assert result["brian_exec_candidate"] == "否"
    assert result["brian_role_candidate"] == "僅管理"


def test_routing_engine_requests_clarification_when_customer_unknown(tmp_path: Path):
    engine = RoutingEngine(_make_resolver(tmp_path))
    result = engine.route(title="完全新案", raw_brief="需要拍攝一場活動")

    assert result["recommended_next_status"] == "clarifying"
    assert "customer_name" in result["missing_fields"]
    assert result["recommended_questions"]


def test_routing_engine_hits_do_not_ask_case(tmp_path: Path):
    engine = RoutingEngine(_make_resolver(tmp_path))
    result = engine.route(title="小白故事線上課程拍攝-台南", raw_brief="永恆少年行銷案源")

    assert result["confidence"] == "high"
    assert "do_not_ask_client_again" in result["matched_rules"]
