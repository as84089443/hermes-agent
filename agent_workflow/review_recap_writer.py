from __future__ import annotations

import json
import secrets
import time
from pathlib import Path
from typing import Any, Optional

from hermes_constants import get_hermes_home

from .sidecar_resolver import EXPORTS_DIR, SidecarResolver

REVIEW_RECAP_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "docs" / "contracts" / "brian-ai-workflow-v1" / "review-recap.schema.json"


class ReviewRecapWriter:
    def __init__(
        self,
        resolver: Optional[SidecarResolver] = None,
        recap_schema_path: Optional[Path] = None,
        exports_dir: Optional[Path] = None,
    ):
        self.resolver = resolver or SidecarResolver(exports_dir=exports_dir)
        self.recap_schema_path = Path(recap_schema_path or REVIEW_RECAP_SCHEMA_PATH)
        self.recap_schema = self._load_json_object(self.recap_schema_path)
        self.exports_dir = Path(exports_dir or EXPORTS_DIR)
        self.vendor_sidecar = self._load_json_list(self.resolver.vendor_sidecar_path)
        self.brand_sidecar = self._load_json_list(self.resolver.brand_sidecar_path)
        self.rulebook = self._load_json_object(self.resolver.rulebook_path)

    def build_recap(self, case: dict[str, Any], context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        now = time.time()
        context = context or {}
        resolution = self.resolver.resolve(
            title=case.get("title", ""),
            customer_name=case.get("customer_name", ""),
            raw_brief=case.get("raw_brief", ""),
        )

        client_owner = case.get("client_owner") or resolution.get("client_owner_candidate") or "待確認"
        pm_owner = case.get("pm_owner") or resolution.get("pm_owner_candidate") or "待確認"
        brian_exec = case.get("brian_exec") or "待確認"
        brian_role = case.get("brian_role") or "待確認"
        brand_or_system = case.get("brand_or_system") or resolution.get("brand_or_system_candidate")
        income_nature = self._infer_income_nature(case, client_owner, pm_owner, brian_exec, brian_role)

        pending_fields = []
        for field_name, value in [
            ("client_owner_final", client_owner),
            ("pm_owner_final", pm_owner),
            ("brian_exec_final", brian_exec),
            ("brian_role_final", brian_role),
            ("income_nature_final", income_nature),
        ]:
            if value in (None, "", "待確認"):
                pending_fields.append(field_name)

        customer_sidecar_update_needed = self._customer_sidecar_update_needed(case, resolution, client_owner)
        brand_sidecar_update_needed = self._brand_sidecar_update_needed(case, resolution, brand_or_system)
        rulebook_update_needed = bool(resolution.get("matched_rulebook_entries") is False) or bool(customer_sidecar_update_needed or brand_sidecar_update_needed)
        do_not_ask_again_candidate = self._do_not_ask_candidate(case, resolution, pending_fields)
        template_candidate, template_reason = self._template_candidate(case)

        recap = {
            "recap_id": f"recap_{case['case_id']}_{secrets.token_hex(4)}",
            "case_id": case["case_id"],
            "created_at": now,
            "created_by": context.get("created_by", "system"),
            "version": 1,
            "case_title": case.get("title"),
            "primary_lane": case.get("primary_lane"),
            "brand_or_system": brand_or_system,
            "customer_name": case.get("customer_name"),
            "client_owner_final": client_owner,
            "pm_owner_final": pm_owner,
            "executor_summary": case.get("executor") or context.get("executor_summary") or "",
            "brian_exec_final": brian_exec,
            "brian_role_final": brian_role,
            "quote_version_final": case.get("quote_version"),
            "artifact_version_final": case.get("artifact_version"),
            "delivered_at": context.get("delivered_at") or case.get("updated_at"),
            "collected_at": context.get("collected_at"),
            "brian_net": context.get("brian_net"),
            "jerry_net": context.get("jerry_net"),
            "chu_post": context.get("chu_post"),
            "income_nature_final": income_nature,
            "change_review_triggered": bool(context.get("change_review_triggered", False)),
            "change_review_summary": context.get("change_review_summary", ""),
            "special_notes": context.get("special_notes") or case.get("notes") or "",
            "incident_flags": context.get("incident_flags", []),
            "customer_sidecar_update_needed": customer_sidecar_update_needed,
            "brand_sidecar_update_needed": brand_sidecar_update_needed,
            "rulebook_update_needed": rulebook_update_needed,
            "do_not_ask_again_candidate": do_not_ask_again_candidate,
            "template_candidate": template_candidate,
            "template_candidate_reason": template_reason,
            "recurring_pattern_candidate": context.get("recurring_pattern_candidate", False),
            "pending_fields": pending_fields,
            "pending_reason": "Missing final routing/business fields" if pending_fields else "",
        }
        self._validate_recap_shape(recap)
        return recap

    def _infer_income_nature(self, case: dict[str, Any], client_owner: str, pm_owner: str, brian_exec: str, brian_role: str) -> str:
        if case.get("primary_lane") == "studio_rental":
            return "資產收入"
        if brian_exec == "是" and brian_role == "支援":
            return "協作支援"
        if client_owner == "共同" and pm_owner == "共同":
            return "共同客戶/共同PM"
        if client_owner == "我" and pm_owner == "我" and brian_exec == "否":
            return "PM/接案"
        if client_owner == "我" and pm_owner == "我" and brian_exec == "是" and brian_role == "主輸出":
            return "兼具PM與執行"
        if brian_exec == "是" and brian_role == "主輸出":
            return "核心執行"
        return "待確認"

    def _customer_sidecar_update_needed(self, case: dict[str, Any], resolution: dict[str, Any], client_owner: str) -> bool:
        if resolution.get("customer_match"):
            return False
        customer_name = (case.get("customer_name") or "").strip()
        if not customer_name:
            return False
        return True

    def _brand_sidecar_update_needed(self, case: dict[str, Any], resolution: dict[str, Any], brand_or_system: Optional[str]) -> bool:
        if resolution.get("brand_match"):
            return False
        return bool(brand_or_system)

    def _do_not_ask_candidate(self, case: dict[str, Any], resolution: dict[str, Any], pending_fields: list[str]) -> bool:
        if resolution.get("do_not_ask_again_hit"):
            return True
        known_case = case.get("title") in set(self.rulebook.get("do_not_ask_client_again", []))
        if known_case:
            return True
        if pending_fields:
            return False
        customer = case.get("customer_name", "")
        if customer and any(
            (entry.get("名稱") == customer and entry.get("confidence") == "high")
            for entry in self.vendor_sidecar
        ):
            return True
        if case.get("brand_or_system") and any(
            (entry.get("name") == case.get("brand_or_system") and entry.get("confidence") == "high")
            for entry in self.brand_sidecar
        ):
            return True
        return False

    def _template_candidate(self, case: dict[str, Any]) -> tuple[bool, str]:
        lane = case.get("primary_lane")
        brand = case.get("brand_or_system")
        if lane == "wedding_private":
            return True, "婚禮線適合沉澱 FAQ、報價套餐與交付模板"
        if lane == "studio_rental":
            return True, "場租線適合沉澱詢價、訂金、行前提醒與 incident 模板"
        if brand in {"麻花影像", "B.W.Studio"}:
            return True, "品牌線具 recurring 特徵，適合沉澱模板"
        return False, ""

    def _validate_recap_shape(self, recap: dict[str, Any]) -> None:
        required = self.recap_schema.get("required_fields", [])
        missing = [field for field in required if field not in recap]
        if missing:
            raise ValueError(f"Recap missing required fields: {missing}")

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
