from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .sidecar_resolver import SidecarResolver


@dataclass
class RoutingResult:
    primary_lane_candidate: str
    client_owner_candidate: Optional[str]
    pm_owner_candidate: Optional[str]
    brian_exec_candidate: Optional[str]
    brian_role_candidate: Optional[str]
    confidence: str
    matched_rules: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    recommended_questions: list[str] = field(default_factory=list)
    recommended_next_status: str = "clarifying"
    recommended_next_owner: str = "Brian"
    brand_or_system_candidate: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_lane_candidate": self.primary_lane_candidate,
            "client_owner_candidate": self.client_owner_candidate,
            "pm_owner_candidate": self.pm_owner_candidate,
            "brian_exec_candidate": self.brian_exec_candidate,
            "brian_role_candidate": self.brian_role_candidate,
            "confidence": self.confidence,
            "matched_rules": list(self.matched_rules),
            "missing_fields": list(self.missing_fields),
            "recommended_questions": list(self.recommended_questions),
            "recommended_next_status": self.recommended_next_status,
            "recommended_next_owner": self.recommended_next_owner,
            "brand_or_system_candidate": self.brand_or_system_candidate,
            "notes": list(self.notes),
        }


class RoutingEngine:
    def __init__(self, resolver: Optional[SidecarResolver] = None):
        self.resolver = resolver or SidecarResolver()

    def route(self, *, title: str = "", customer_name: str = "", raw_brief: str = "") -> dict[str, Any]:
        resolution = self.resolver.resolve(title=title, customer_name=customer_name, raw_brief=raw_brief)
        haystack = " ".join(part for part in [title, customer_name, raw_brief] if part).strip()
        haystack_lower = haystack.lower()

        lane = self._detect_lane(haystack_lower, resolution.get("brand_or_system_candidate"))
        client_owner = resolution.get("client_owner_candidate")
        pm_owner = resolution.get("pm_owner_candidate")
        brand_or_system = resolution.get("brand_or_system_candidate")
        matched_rules = list(resolution.get("matched_rulebook_entries", []))
        notes = list(resolution.get("notes", []))

        brian_exec, brian_role = self._detect_execution_mode(haystack_lower)

        missing_fields = []
        recommended_questions = []

        if not customer_name.strip() and not resolution.get("customer_match"):
            missing_fields.append("customer_name")
            recommended_questions.append("這是誰的客戶／客戶是誰？")

        if client_owner is None:
            missing_fields.append("client_owner")
            recommended_questions.append("這案是你的客戶、共同客戶，還是上游合作方？")

        if lane == "commercial" and brian_exec is None:
            missing_fields.append("brian_exec")
            recommended_questions.append("這案需要 Brian 親自下場嗎？")

        next_status = "ready_for_quote" if not missing_fields else "clarifying"
        confidence = resolution.get("confidence", "low")
        if missing_fields and confidence == "high" and not resolution.get("do_not_ask_again_hit"):
            confidence = "medium"

        return RoutingResult(
            primary_lane_candidate=lane,
            client_owner_candidate=client_owner,
            pm_owner_candidate=pm_owner,
            brian_exec_candidate=brian_exec,
            brian_role_candidate=brian_role,
            confidence=confidence,
            matched_rules=matched_rules,
            missing_fields=missing_fields,
            recommended_questions=recommended_questions,
            recommended_next_status=next_status,
            recommended_next_owner="Brian",
            brand_or_system_candidate=brand_or_system,
            notes=notes,
        ).to_dict()

    def _detect_lane(self, haystack_lower: str, brand: Optional[str]) -> str:
        if brand in {"麻花影像", "VAF美式婚紗"}:
            return "wedding_private"
        if any(k in haystack_lower for k in ["租棚", "場租", "棚租"]):
            return "studio_rental"
        if any(k in haystack_lower for k in ["婚禮", "午宴", "早儀", "婚攝", "抓周", "sde"]):
            return "wedding_private"
        if any(k in haystack_lower for k in ["後製", "剪輯", "修片"]):
            return "post_only"
        if any(k in haystack_lower for k in ["共同客戶", "共同pm"]):
            return "collab_ops"
        return "commercial"

    def _detect_execution_mode(self, haystack_lower: str) -> tuple[Optional[str], Optional[str]]:
        if any(k in haystack_lower for k in ["外發", "發給", "交給他拍", "交給他做"]):
            return "否", "僅管理"
        if any(k in haystack_lower for k in ["助理", "支援", "陪跑"]):
            return "是", "支援"
        if any(k in haystack_lower for k in ["brian單機", "brian平面", "brian導播", "主拍", "主攝", "拍攝", "直播", "平面", "動態"]):
            return "是", "主輸出"
        return None, None
