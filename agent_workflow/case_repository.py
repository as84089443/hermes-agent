from __future__ import annotations

import json
import secrets
import time
from typing import Any, Dict, Optional

from .case_models import CaseRecord
from .case_state_machine import ensure_valid_transition
from .case_validation import validate_create_payload, validate_update_patch
from .storage import WorkflowStorage, _DB_LOCK


def _utc_now() -> float:
    return time.time()


class CaseRepository:
    def __init__(self, storage: Optional[WorkflowStorage] = None):
        self.storage = storage or WorkflowStorage()
        self.conn = self.storage.conn

    def close(self) -> None:
        self.storage.close()

    def create_case(self, **payload: Any) -> Dict[str, Any]:
        now = _utc_now()
        record = {
            "case_id": payload.get("case_id") or f"case_{int(now)}_{secrets.token_hex(4)}",
            "title": payload["title"],
            "source": payload["source"],
            "customer_name": payload["customer_name"],
            "primary_lane": payload["primary_lane"],
            "status": payload.get("status", "intake"),
            "current_owner": payload["current_owner"],
            "next_action": payload["next_action"],
            "next_owner": payload["next_owner"],
            "created_at": payload.get("created_at", now),
            "updated_at": payload.get("updated_at", now),
            "client_owner": payload.get("client_owner"),
            "pm_owner": payload.get("pm_owner"),
            "brian_exec": payload.get("brian_exec"),
            "brian_role": payload.get("brian_role"),
            "brand_or_system": payload.get("brand_or_system"),
            "raw_brief": payload.get("raw_brief"),
            "normalized_brief": payload.get("normalized_brief"),
            "budget_status": payload.get("budget_status"),
            "due_date": payload.get("due_date"),
            "executor": payload.get("executor"),
            "approver": payload.get("approver"),
            "quote_version": payload.get("quote_version"),
            "artifact_version": payload.get("artifact_version"),
            "notes": payload.get("notes"),
            "risk_flags": payload.get("risk_flags", []),
            "parent_case_id": payload.get("parent_case_id"),
            "project_group_id": payload.get("project_group_id"),
            "sidecar_type": payload.get("sidecar_type"),
            "scope_locked_at": payload.get("scope_locked_at"),
            "approved_at": payload.get("approved_at"),
            "accepted_at": payload.get("accepted_at"),
            "closed_at": payload.get("closed_at"),
            "lost_reason": payload.get("lost_reason"),
        }
        validate_create_payload(record)
        with _DB_LOCK:
            self.conn.execute(
                """
                INSERT INTO cases (
                    case_id, title, source, customer_name, primary_lane, status,
                    current_owner, next_action, next_owner, client_owner, pm_owner,
                    brian_exec, brian_role, brand_or_system, raw_brief, normalized_brief,
                    budget_status, due_date, executor, approver, quote_version,
                    artifact_version, notes, risk_flags_json, parent_case_id,
                    project_group_id, sidecar_type, scope_locked_at, approved_at,
                    accepted_at, closed_at, lost_reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["case_id"],
                    record["title"].strip(),
                    record["source"].strip(),
                    record["customer_name"].strip(),
                    record["primary_lane"],
                    record["status"],
                    record["current_owner"].strip(),
                    record["next_action"].strip(),
                    record["next_owner"].strip(),
                    record["client_owner"],
                    record["pm_owner"],
                    record["brian_exec"],
                    record["brian_role"],
                    record["brand_or_system"],
                    record["raw_brief"],
                    record["normalized_brief"],
                    record["budget_status"],
                    record["due_date"],
                    record["executor"],
                    record["approver"],
                    record["quote_version"],
                    record["artifact_version"],
                    record["notes"],
                    json.dumps(record["risk_flags"], ensure_ascii=False),
                    record["parent_case_id"],
                    record["project_group_id"],
                    record["sidecar_type"],
                    record["scope_locked_at"],
                    record["approved_at"],
                    record["accepted_at"],
                    record["closed_at"],
                    record["lost_reason"],
                    record["created_at"],
                    record["updated_at"],
                ),
            )
            self.conn.commit()
        return self.get_case(record["case_id"])

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        return self._row_to_dict(row)

    def list_cases(
        self,
        *,
        status: Optional[str] = None,
        lane: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        where = []
        params: list[Any] = []
        if status:
            where.append("status = ?")
            params.append(status)
        if lane:
            where.append("primary_lane = ?")
            params.append(lane)
        if owner:
            where.append("current_owner = ?")
            params.append(owner)
        sql = "SELECT * FROM cases"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def update_case_fields(self, case_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        validate_update_patch(patch)
        if not self.get_case(case_id):
            raise KeyError(f"Case not found: {case_id}")
        patch = dict(patch)
        patch["updated_at"] = _utc_now()
        if "risk_flags" in patch:
            patch["risk_flags_json"] = json.dumps(patch.pop("risk_flags"), ensure_ascii=False)
        assignments = ", ".join(f"{field} = ?" for field in patch.keys())
        params = list(patch.values()) + [case_id]
        with _DB_LOCK:
            self.conn.execute(f"UPDATE cases SET {assignments} WHERE case_id = ?", params)
            self.conn.commit()
        return self.get_case(case_id)

    def transition_case(self, case_id: str, to_status: str, reason: Optional[str] = None) -> Dict[str, Any]:
        current = self.get_case(case_id)
        if not current:
            raise KeyError(f"Case not found: {case_id}")
        ensure_valid_transition(current["status"], to_status)
        patch: Dict[str, Any] = {"status": to_status}
        now = _utc_now()
        if to_status == "confirmed" and not current.get("scope_locked_at"):
            patch["scope_locked_at"] = now
        if to_status == "closed":
            patch["closed_at"] = now
        if to_status == "lost":
            patch["lost_reason"] = reason
        return self._transition_patch(case_id, patch)

    def _transition_patch(self, case_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        patch = dict(patch)
        patch["updated_at"] = _utc_now()
        assignments = ", ".join(f"{field} = ?" for field in patch.keys())
        params = list(patch.values()) + [case_id]
        with _DB_LOCK:
            self.conn.execute(f"UPDATE cases SET {assignments} WHERE case_id = ?", params)
            self.conn.commit()
        return self.get_case(case_id)

    def _row_to_dict(self, row: Any) -> Dict[str, Any]:
        data = dict(row)
        data["risk_flags"] = json.loads(data.pop("risk_flags_json") or "[]")
        return data
