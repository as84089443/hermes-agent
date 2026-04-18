from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from hermes_constants import get_hermes_home

EXPORTS_DIR = get_hermes_home() / "exports" / "google_calendar_history"
VENDOR_SIDECAR_GLOB = "vendor_master_sidecar_v*.json"
BRAND_SIDECAR_GLOB = "customer_brand_sidecar_v*.json"
RULEBOOK_GLOB = "analysis_rulebook_v*.json"


@dataclass
class SidecarResolution:
    customer_match: Optional[dict[str, Any]] = None
    brand_match: Optional[dict[str, Any]] = None
    matched_rulebook_entries: list[str] = field(default_factory=list)
    do_not_ask_again_hit: bool = False
    confidence: str = "low"
    client_owner_candidate: Optional[str] = None
    pm_owner_candidate: Optional[str] = None
    brand_or_system_candidate: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_match": self.customer_match,
            "brand_match": self.brand_match,
            "matched_rulebook_entries": list(self.matched_rulebook_entries),
            "do_not_ask_again_hit": self.do_not_ask_again_hit,
            "confidence": self.confidence,
            "client_owner_candidate": self.client_owner_candidate,
            "pm_owner_candidate": self.pm_owner_candidate,
            "brand_or_system_candidate": self.brand_or_system_candidate,
            "notes": list(self.notes),
        }


class SidecarResolver:
    def __init__(
        self,
        exports_dir: Optional[Path] = None,
        vendor_sidecar_path: Optional[Path] = None,
        brand_sidecar_path: Optional[Path] = None,
        rulebook_path: Optional[Path] = None,
    ):
        self.exports_dir = Path(exports_dir or EXPORTS_DIR)
        self.vendor_sidecar_path = vendor_sidecar_path or self._latest_file(VENDOR_SIDECAR_GLOB)
        self.brand_sidecar_path = brand_sidecar_path or self._latest_file(BRAND_SIDECAR_GLOB)
        self.rulebook_path = rulebook_path or self._latest_file(RULEBOOK_GLOB)
        self.vendor_sidecar = self._load_json_list(self.vendor_sidecar_path)
        self.brand_sidecar = self._load_json_list(self.brand_sidecar_path)
        self.rulebook = self._load_json_object(self.rulebook_path)

    def resolve(self, *, title: str = "", customer_name: str = "", raw_brief: str = "") -> dict[str, Any]:
        haystack = " ".join(part for part in [title, customer_name, raw_brief] if part).strip()
        haystack_lower = haystack.lower()
        resolution = SidecarResolution()

        customer_match = self._match_customer(haystack_lower)
        if customer_match:
            resolution.customer_match = customer_match
            resolution.client_owner_candidate = customer_match.get("client_owner_guess") or customer_match.get("owner_guess")
            resolution.pm_owner_candidate = customer_match.get("pm_owner_guess") or customer_match.get("pm_guess")
            resolution.notes.append(f"customer sidecar match: {customer_match.get('名稱') or customer_match.get('customer_name')}")

        brand_match = self._match_brand(haystack_lower)
        if brand_match:
            resolution.brand_match = brand_match
            resolution.brand_or_system_candidate = brand_match.get("name") or brand_match.get("brand_name")
            if not resolution.client_owner_candidate:
                resolution.client_owner_candidate = brand_match.get("owner_type_guess")
            if not resolution.pm_owner_candidate:
                resolution.pm_owner_candidate = brand_match.get("pm_owner_guess")
            resolution.notes.append(f"brand sidecar match: {resolution.brand_or_system_candidate}")

        do_not_ask = self.rulebook.get("do_not_ask_client_again", [])
        resolution.do_not_ask_again_hit = any(entry.lower() in haystack_lower for entry in do_not_ask)
        if resolution.do_not_ask_again_hit:
            resolution.matched_rulebook_entries.append("do_not_ask_client_again")
            resolution.notes.append("matched do-not-ask-again case")

        confirmed_lines = self.rulebook.get("confirmed_client_lines", {})
        for key, note in confirmed_lines.items():
            if key.lower() in haystack_lower:
                resolution.matched_rulebook_entries.append(key)
                resolution.notes.append(f"rulebook confirmed line: {key}")
                if not resolution.client_owner_candidate and "shared" not in note.lower() and "共同" not in note:
                    resolution.client_owner_candidate = "我"
                    resolution.pm_owner_candidate = resolution.pm_owner_candidate or "我"
                elif not resolution.client_owner_candidate and ("shared" in note.lower() or "共同" in note):
                    resolution.client_owner_candidate = "共同"
                    resolution.pm_owner_candidate = resolution.pm_owner_candidate or "共同"

        resolution.confidence = self._resolve_confidence(resolution)
        return resolution.to_dict()

    def _resolve_confidence(self, resolution: SidecarResolution) -> str:
        if resolution.do_not_ask_again_hit:
            return "high"
        if resolution.customer_match and resolution.customer_match.get("confidence") == "high":
            return "high"
        if resolution.brand_match and resolution.brand_match.get("confidence") == "high":
            return "high"
        if resolution.customer_match or resolution.brand_match or resolution.matched_rulebook_entries:
            return "medium"
        return "low"

    def _match_customer(self, haystack_lower: str) -> Optional[dict[str, Any]]:
        for item in self.vendor_sidecar:
            names = [item.get("名稱", "")]
            contact = item.get("匯款接洽人", "")
            if contact:
                names.extend(part.strip() for part in contact.replace("\n", ",").split(",") if part.strip())
            for name in names:
                if name and name.lower() in haystack_lower:
                    return item
        return None

    def _match_brand(self, haystack_lower: str) -> Optional[dict[str, Any]]:
        for item in self.brand_sidecar:
            names = [item.get("name", "")]
            aliases = item.get("aliases", []) or []
            names.extend(aliases)
            for name in names:
                if name and name.lower() in haystack_lower:
                    return item
        return None

    def _latest_file(self, pattern: str) -> Optional[Path]:
        matches = sorted(self.exports_dir.glob(pattern))
        return matches[-1] if matches else None

    @staticmethod
    def _load_json_list(path: Optional[Path]) -> list[dict[str, Any]]:
        if not path or not Path(path).exists():
            return []
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []

    @staticmethod
    def _load_json_object(path: Optional[Path]) -> dict[str, Any]:
        if not path or not Path(path).exists():
            return {}
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
