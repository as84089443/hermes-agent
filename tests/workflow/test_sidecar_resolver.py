from __future__ import annotations

import json
from pathlib import Path

from agent_workflow.sidecar_resolver import SidecarResolver


def _write_json(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def test_sidecar_resolver_matches_customer_sidecar(tmp_path: Path):
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
    result = resolver.resolve(title="碼非直播-操機", raw_brief="Jeffrey 說這案要先對一下")

    assert result["client_owner_candidate"] == "我"
    assert result["pm_owner_candidate"] == "我"
    assert result["confidence"] == "high"
    assert result["customer_match"]["名稱"] == "碼非創意企業有限公司"



def test_sidecar_resolver_matches_brand_sidecar(tmp_path: Path):
    exports = tmp_path / "exports"
    exports.mkdir()
    _write_json(exports / "vendor_master_sidecar_v1.json", [])
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
    _write_json(exports / "analysis_rulebook_v1.json", {"do_not_ask_client_again": [], "confirmed_client_lines": {}})

    resolver = SidecarResolver(exports_dir=exports)
    result = resolver.resolve(title="麻花婚禮午宴", raw_brief="婚禮平面與動態")

    assert result["brand_or_system_candidate"] == "麻花影像"
    assert result["client_owner_candidate"] == "共同"
    assert result["pm_owner_candidate"] == "共同"
    assert result["confidence"] == "high"



def test_sidecar_resolver_hits_do_not_ask_rulebook(tmp_path: Path):
    exports = tmp_path / "exports"
    exports.mkdir()
    _write_json(exports / "vendor_master_sidecar_v1.json", [])
    _write_json(exports / "customer_brand_sidecar_v1.json", [])
    _write_json(
        exports / "analysis_rulebook_v1.json",
        {
            "do_not_ask_client_again": ["小白故事線上課程拍攝-台南"],
            "confirmed_client_lines": {"永恆少年行銷": "Brian direct client line"},
        },
    )

    resolver = SidecarResolver(exports_dir=exports)
    result = resolver.resolve(title="小白故事線上課程拍攝-台南", raw_brief="永恆少年行銷案源")

    assert result["do_not_ask_again_hit"] is True
    assert result["confidence"] == "high"
    assert "永恆少年行銷" in result["matched_rulebook_entries"]
    assert result["client_owner_candidate"] == "我"



def test_sidecar_resolver_returns_low_when_no_match(tmp_path: Path):
    exports = tmp_path / "exports"
    exports.mkdir()
    _write_json(exports / "vendor_master_sidecar_v1.json", [])
    _write_json(exports / "customer_brand_sidecar_v1.json", [])
    _write_json(exports / "analysis_rulebook_v1.json", {})

    resolver = SidecarResolver(exports_dir=exports)
    result = resolver.resolve(title="完全未知案子")

    assert result["confidence"] == "low"
    assert result["customer_match"] is None
    assert result["brand_match"] is None
