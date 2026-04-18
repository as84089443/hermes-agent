from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.do_not_ask_detector import DoNotAskCandidateDetector
from agent_workflow.review_recap_writer import ReviewRecapWriter
from agent_workflow.sidecar_resolver import SidecarResolver


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_stack(tmp_path: Path):
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
            },
        },
    )
    resolver = SidecarResolver(exports_dir=exports)
    writer = ReviewRecapWriter(resolver=resolver, exports_dir=exports)
    detector = DoNotAskCandidateDetector(resolver=resolver, exports_dir=exports)
    return writer, detector



def test_do_not_ask_detector_hits_existing_rulebook_case(tmp_path: Path):
    writer, detector = _make_stack(tmp_path)
    case = {
        "case_id": "case_1",
        "title": "小白故事線上課程拍攝-台南",
        "customer_name": "永恆少年行銷",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "否",
        "brian_role": "僅管理",
        "primary_lane": "commercial",
    }
    recap = writer.build_recap(case)
    result = detector.detect(case=case, recap=recap)

    assert result["candidate"] is True
    assert result["confidence"] == "high"
    assert "already_in_rulebook" in result["reason_codes"]



def test_do_not_ask_detector_promotes_high_conf_customer_line(tmp_path: Path):
    writer, detector = _make_stack(tmp_path)
    case = {
        "case_id": "case_2",
        "title": "碼非直播-操機",
        "customer_name": "碼非創意企業有限公司",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "是",
        "brian_role": "主輸出",
        "primary_lane": "commercial",
    }
    recap = writer.build_recap(case)
    result = detector.detect(case=case, recap=recap)

    assert result["candidate"] is True
    assert result["confidence"] == "high"
    assert "high_conf_customer_sidecar" in result["reason_codes"]



def test_do_not_ask_detector_uses_brand_context(tmp_path: Path):
    writer, detector = _make_stack(tmp_path)
    case = {
        "case_id": "case_3",
        "title": "麻花婚禮午宴",
        "customer_name": "新娘新郎",
        "brand_or_system": "麻花影像",
        "client_owner": "共同",
        "pm_owner": "共同",
        "brian_exec": "是",
        "brian_role": "主輸出",
        "primary_lane": "wedding_private",
    }
    recap = writer.build_recap(case)
    result = detector.detect(case=case, recap=recap)

    assert result["candidate"] is True
    assert "high_conf_brand_sidecar" in result["reason_codes"]



def test_do_not_ask_detector_returns_false_for_weak_case(tmp_path: Path):
    writer, detector = _make_stack(tmp_path)
    case = {
        "case_id": "case_4",
        "title": "全新未知案",
        "customer_name": "陌生客戶",
        "primary_lane": "commercial",
    }
    recap = writer.build_recap(case)
    result = detector.detect(case=case, recap=recap)

    assert result["candidate"] is False
    assert result["confidence"] == "low"
