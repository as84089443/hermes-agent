from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.review_recap_writer import ReviewRecapWriter
from agent_workflow.sidecar_resolver import SidecarResolver


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_writer(tmp_path: Path) -> ReviewRecapWriter:
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
    return ReviewRecapWriter(resolver=resolver, exports_dir=exports)


def test_review_recap_writer_complete_case_no_pending(tmp_path: Path):
    writer = _make_writer(tmp_path)
    case = {
        "case_id": "case_1",
        "title": "碼非直播-操機",
        "primary_lane": "commercial",
        "customer_name": "碼非創意企業有限公司",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "是",
        "brian_role": "主輸出",
        "quote_version": "qv_1",
        "artifact_version": "av_1",
        "updated_at": 1.0,
    }
    recap = writer.build_recap(case, {"created_by": "Brian"})

    assert recap["pending_fields"] == []
    assert recap["income_nature_final"] == "兼具PM與執行"
    assert recap["customer_sidecar_update_needed"] is False



def test_review_recap_writer_missing_client_owner_marks_pending(tmp_path: Path):
    writer = _make_writer(tmp_path)
    case = {
        "case_id": "case_2",
        "title": "新客活動拍攝",
        "primary_lane": "commercial",
        "customer_name": "新客戶",
        "pm_owner": "我",
        "brian_exec": "是",
        "brian_role": "主輸出",
        "updated_at": 1.0,
    }
    recap = writer.build_recap(case)

    assert "client_owner_final" in recap["pending_fields"]
    assert recap["customer_sidecar_update_needed"] is True



def test_review_recap_writer_studio_rental_sets_asset_income(tmp_path: Path):
    writer = _make_writer(tmp_path)
    case = {
        "case_id": "case_3",
        "title": "租棚-品牌拍攝",
        "primary_lane": "studio_rental",
        "customer_name": "租戶A",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "否",
        "brian_role": "僅管理",
        "updated_at": 1.0,
    }
    recap = writer.build_recap(case)

    assert recap["income_nature_final"] == "資產收入"
    assert recap["template_candidate"] is True



def test_review_recap_writer_wedding_brand_detects_brand_context(tmp_path: Path):
    writer = _make_writer(tmp_path)
    case = {
        "case_id": "case_4",
        "title": "麻花婚禮午宴",
        "primary_lane": "wedding_private",
        "customer_name": "新娘新郎",
        "client_owner": "共同",
        "pm_owner": "共同",
        "brian_exec": "是",
        "brian_role": "主輸出",
        "updated_at": 1.0,
    }
    recap = writer.build_recap(case)

    assert recap["brand_or_system"] == "麻花影像"
    assert recap["brand_sidecar_update_needed"] is False
    assert recap["template_candidate"] is True



def test_review_recap_writer_do_not_ask_candidate_for_known_case(tmp_path: Path):
    writer = _make_writer(tmp_path)
    case = {
        "case_id": "case_5",
        "title": "小白故事線上課程拍攝-台南",
        "primary_lane": "commercial",
        "customer_name": "永恆少年行銷",
        "client_owner": "我",
        "pm_owner": "我",
        "brian_exec": "否",
        "brian_role": "僅管理",
        "updated_at": 1.0,
    }
    recap = writer.build_recap(case)

    assert recap["do_not_ask_again_candidate"] is True
    assert recap["income_nature_final"] == "PM/接案"
