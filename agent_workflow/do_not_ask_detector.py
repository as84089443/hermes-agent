from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .sidecar_resolver import EXPORTS_DIR, SidecarResolver


class DoNotAskCandidateDetector:
    def __init__(self, resolver: Optional[SidecarResolver] = None, exports_dir: Optional[Path] = None):
        self.resolver = resolver or SidecarResolver(exports_dir=exports_dir)
        self.exports_dir = Path(exports_dir or EXPORTS_DIR)
        self.rulebook = self._load_json_object(self.resolver.rulebook_path)
        self.vendor_sidecar = self._load_json_list(self.resolver.vendor_sidecar_path)
        self.brand_sidecar = self._load_json_list(self.resolver.brand_sidecar_path)

    def detect(self, *, case: dict[str, Any], recap: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        recap = recap or {}
        title = case.get("title", "")
        customer_name = case.get("customer_name", "")
        brand = case.get("brand_or_system") or recap.get("brand_or_system")

        reasons: list[str] = []
        candidate = False
        confidence = "low"

        existing = set(self.rulebook.get("do_not_ask_client_again", []))
        if title in existing:
            return {
                "candidate": True,
                "confidence": "high",
                "reason_codes": ["already_in_rulebook"],
                "notes": ["Case already present in do-not-ask rulebook."],
            }

        if recap.get("do_not_ask_again_candidate") is True:
            candidate = True
            reasons.append("recap_flagged")

        if customer_name and any(
            entry.get("名稱") == customer_name and entry.get("confidence") == "high"
            for entry in self.vendor_sidecar
        ):
            candidate = True
            reasons.append("high_conf_customer_sidecar")

        if brand and any(
            entry.get("name") == brand and entry.get("confidence") == "high"
            for entry in self.brand_sidecar
        ):
            candidate = True
            reasons.append("high_conf_brand_sidecar")

        if case.get("client_owner") == "我" and case.get("pm_owner") == "我" and case.get("brian_exec") in {"是", "否"}:
            candidate = True
            reasons.append("stable_core_fields")

        if candidate:
            if "recap_flagged" in reasons or "high_conf_customer_sidecar" in reasons or "high_conf_brand_sidecar" in reasons:
                confidence = "high"
            else:
                confidence = "medium"

        notes = []
        if customer_name:
            notes.append(f"customer={customer_name}")
        if brand:
            notes.append(f"brand={brand}")
        if case.get("client_owner"):
            notes.append(f"client_owner={case.get('client_owner')}")
        if case.get("pm_owner"):
            notes.append(f"pm_owner={case.get('pm_owner')}")

        return {
            "candidate": candidate,
            "confidence": confidence,
            "reason_codes": reasons,
            "notes": notes,
        }

    @staticmethod
    def _load_json_object(path: Optional[Path]) -> dict[str, Any]:
        if not path or not Path(path).exists():
            return {}
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _load_json_list(path: Optional[Path]) -> list[dict[str, Any]]:
        if not path or not Path(path).exists():
            return []
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
