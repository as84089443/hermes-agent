from __future__ import annotations

import secrets
import time
from typing import Any, Optional


class RoutingMismatchTracker:
    def build_mismatch(
        self,
        *,
        case: dict[str, Any],
        routing_result: dict[str, Any],
        final_values: dict[str, Any],
        human_explanation: str = "",
    ) -> dict[str, Any]:
        now = time.time()
        mismatched_fields: list[str] = []

        field_map = {
            "primary_lane": (routing_result.get("primary_lane_candidate"), final_values.get("primary_lane")),
            "client_owner": (routing_result.get("client_owner_candidate"), final_values.get("client_owner")),
            "pm_owner": (routing_result.get("pm_owner_candidate"), final_values.get("pm_owner")),
            "brian_exec": (routing_result.get("brian_exec_candidate"), final_values.get("brian_exec")),
            "brian_role": (routing_result.get("brian_role_candidate"), final_values.get("brian_role")),
        }
        for field, (system_val, final_val) in field_map.items():
            if final_val is not None and system_val != final_val:
                mismatched_fields.append(field)

        mismatch_type = self._infer_mismatch_type(mismatched_fields)
        root_cause_guess = self._infer_root_cause(case, routing_result, final_values, human_explanation, mismatched_fields)

        record = {
            "mismatch_id": f"mm_{case['case_id']}_{secrets.token_hex(4)}",
            "case_id": case["case_id"],
            "created_at": now,
            "created_by": final_values.get("created_by", "human"),
            "status_at_detection": case.get("status"),
            "case_title": case.get("title"),
            "raw_brief": case.get("raw_brief"),
            "customer_name": case.get("customer_name"),
            "brand_or_system": case.get("brand_or_system"),
            "source": case.get("source"),
            "primary_lane_at_detection": case.get("primary_lane"),
            "system_lane_candidate": routing_result.get("primary_lane_candidate"),
            "system_client_owner_candidate": routing_result.get("client_owner_candidate"),
            "system_pm_owner_candidate": routing_result.get("pm_owner_candidate"),
            "system_brian_exec_candidate": routing_result.get("brian_exec_candidate"),
            "system_brian_role_candidate": routing_result.get("brian_role_candidate"),
            "system_confidence": routing_result.get("confidence"),
            "system_matched_rules": routing_result.get("matched_rules", []),
            "system_missing_fields": routing_result.get("missing_fields", []),
            "final_lane": final_values.get("primary_lane"),
            "final_client_owner": final_values.get("client_owner"),
            "final_pm_owner": final_values.get("pm_owner"),
            "final_brian_exec": final_values.get("brian_exec"),
            "final_brian_role": final_values.get("brian_role"),
            "mismatched_fields": mismatched_fields,
            "mismatch_type": mismatch_type,
            "root_cause_guess": root_cause_guess,
            "human_explanation": human_explanation,
            "customer_sidecar_update_needed": root_cause_guess in {"missing_customer_sidecar", "human_only_business_context"},
            "brand_sidecar_update_needed": root_cause_guess == "missing_brand_sidecar",
            "rulebook_update_needed": bool(mismatched_fields),
            "do_not_ask_candidate": root_cause_guess in {"missing_do_not_ask_rule", "human_only_business_context"},
            "routing_prompt_eval_candidate": bool(mismatched_fields) and root_cause_guess in {"heuristic_overreach", "ambiguous_raw_brief", "human_only_business_context"},
            "resolved": bool(mismatched_fields),
            "resolution_note": self._resolution_note(mismatched_fields, root_cause_guess),
        }
        return record

    def _infer_mismatch_type(self, mismatched_fields: list[str]) -> str:
        if not mismatched_fields:
            return "insufficient_context"
        if len(mismatched_fields) > 1:
            return "multi_factor"
        field = mismatched_fields[0]
        return {
            "client_owner": "customer_ownership_error",
            "pm_owner": "pm_ownership_error",
            "primary_lane": "lane_error",
            "brian_exec": "execution_role_error",
            "brian_role": "execution_role_error",
        }.get(field, "insufficient_context")

    def _infer_root_cause(
        self,
        case: dict[str, Any],
        routing_result: dict[str, Any],
        final_values: dict[str, Any],
        human_explanation: str,
        mismatched_fields: list[str],
    ) -> str:
        if not mismatched_fields:
            return "unknown"
        if routing_result.get("system_missing_fields"):
            return "insufficient_context"
        text = " ".join(
            str(x)
            for x in [case.get("raw_brief", ""), human_explanation, case.get("title", "")]
            if x
        ).lower()
        if any(k in text for k in ["麻花", "品牌", "vaf"]) and "brand_or_system" in mismatched_fields:
            return "missing_brand_sidecar"
        if any(k in text for k in ["上游", "三立", "永恆少年", "錨點", "bni", "夥伴", "舊同事", "介紹"]) :
            return "human_only_business_context"
        if any(k in text for k in ["客戶", "我的", "共同"]) and "client_owner" in mismatched_fields:
            return "missing_customer_sidecar"
        return "heuristic_overreach"

    def _resolution_note(self, mismatched_fields: list[str], root_cause_guess: str) -> str:
        if not mismatched_fields:
            return "No routing mismatch detected."
        return f"Mismatch on {', '.join(mismatched_fields)}; likely cause={root_cause_guess}."
