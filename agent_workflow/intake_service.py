from __future__ import annotations

from typing import Any, Optional

from .case_repository import CaseRepository
from .routing_engine import RoutingEngine


class IntakeService:
    def __init__(
        self,
        repository: Optional[CaseRepository] = None,
        routing_engine: Optional[RoutingEngine] = None,
    ):
        self.repository = repository or CaseRepository()
        self.routing_engine = routing_engine or RoutingEngine()

    def close(self) -> None:
        self.repository.close()

    def build_case_draft(
        self,
        *,
        title: str,
        source: str,
        raw_brief: str,
        customer_name: str = "",
        created_by: str = "Brian",
    ) -> dict[str, Any]:
        routing = self.routing_engine.route(
            title=title,
            customer_name=customer_name,
            raw_brief=raw_brief,
        )
        draft = {
            "title": title,
            "source": source,
            "customer_name": customer_name or self._fallback_customer_name(title, raw_brief),
            "primary_lane": routing["primary_lane_candidate"],
            "status": routing["recommended_next_status"],
            "current_owner": routing["recommended_next_owner"],
            "next_action": self._next_action_from_routing(routing),
            "next_owner": routing["recommended_next_owner"],
            "client_owner": routing.get("client_owner_candidate"),
            "pm_owner": routing.get("pm_owner_candidate"),
            "brian_exec": routing.get("brian_exec_candidate"),
            "brian_role": routing.get("brian_role_candidate"),
            "brand_or_system": routing.get("brand_or_system_candidate"),
            "raw_brief": raw_brief,
            "normalized_brief": self._build_normalized_brief(title, raw_brief, routing),
            "notes": self._build_notes(created_by, routing),
            "risk_flags": self._build_risk_flags(routing),
            "routing_result": routing,
        }
        return draft

    def create_case_from_intake(
        self,
        *,
        title: str,
        source: str,
        raw_brief: str,
        customer_name: str = "",
        created_by: str = "Brian",
    ) -> dict[str, Any]:
        draft = self.build_case_draft(
            title=title,
            source=source,
            raw_brief=raw_brief,
            customer_name=customer_name,
            created_by=created_by,
        )
        create_payload = {k: v for k, v in draft.items() if k != "routing_result"}
        return self.repository.create_case(**create_payload)

    def _fallback_customer_name(self, title: str, raw_brief: str) -> str:
        if title.strip():
            return title.strip()
        brief = raw_brief.strip()
        return brief[:80] if brief else "待確認客戶"

    def _next_action_from_routing(self, routing: dict[str, Any]) -> str:
        questions = routing.get("recommended_questions") or []
        if questions:
            return f"補問：{'；'.join(questions[:2])}"
        return "進入報價/接案判斷"

    def _build_normalized_brief(self, title: str, raw_brief: str, routing: dict[str, Any]) -> str:
        parts = [f"案件：{title}", f"主 lane 候選：{routing['primary_lane_candidate']}"]
        if raw_brief.strip():
            parts.append(f"摘要：{raw_brief.strip()}")
        if routing.get("brand_or_system_candidate"):
            parts.append(f"品牌/系統：{routing['brand_or_system_candidate']}")
        return "\n".join(parts)

    def _build_notes(self, created_by: str, routing: dict[str, Any]) -> str:
        notes = [f"intake created by: {created_by}"]
        if routing.get("notes"):
            notes.extend(routing["notes"])
        return " | ".join(notes)

    def _build_risk_flags(self, routing: dict[str, Any]) -> list[str]:
        flags = []
        if routing.get("missing_fields"):
            flags.append("missing_key_fields")
        if routing.get("confidence") == "low":
            flags.append("low_routing_confidence")
        return flags
