from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

CLIENT_OWNER_VALUES = ("我", "Jerry", "共同", "其他", "待確認")
PM_OWNER_VALUES = ("我", "Jerry", "共同", "其他", "待確認")
BRIAN_EXEC_VALUES = ("是", "否", "待確認")
BRIAN_ROLE_VALUES = ("主輸出", "支援", "僅管理", "未參與", "待確認")
PRIMARY_LANE_VALUES = ("commercial", "wedding_private", "studio_rental", "post_only", "collab_ops")
STATUS_VALUES = (
    "intake",
    "clarifying",
    "ready_for_quote",
    "quote_sent",
    "soft_hold",
    "confirmed",
    "in_execution",
    "delivered",
    "billing",
    "collected",
    "closed",
    "lost",
)
BUDGET_STATUS_VALUES = ("unknown", "needs_quote", "quoted", "approved", "internal")
SIDECAR_TYPE_VALUES = ("none", "client_sidecar", "brand_sidecar", "internal_sidecar")

REQUIRED_FIELDS = (
    "case_id",
    "title",
    "source",
    "customer_name",
    "primary_lane",
    "status",
    "current_owner",
    "next_action",
    "next_owner",
    "created_at",
    "updated_at",
)

IMMUTABLE_FIELDS = ("case_id", "created_at")


@dataclass
class CaseRecord:
    case_id: str
    title: str
    source: str
    customer_name: str
    primary_lane: str
    status: str
    current_owner: str
    next_action: str
    next_owner: str
    created_at: float
    updated_at: float

    client_owner: Optional[str] = None
    pm_owner: Optional[str] = None
    brian_exec: Optional[str] = None
    brian_role: Optional[str] = None
    brand_or_system: Optional[str] = None
    raw_brief: Optional[str] = None
    normalized_brief: Optional[str] = None
    budget_status: Optional[str] = None
    due_date: Optional[str] = None
    executor: Optional[str] = None
    approver: Optional[str] = None
    quote_version: Optional[str] = None
    artifact_version: Optional[str] = None
    notes: Optional[str] = None
    risk_flags: list[str] = field(default_factory=list)
    parent_case_id: Optional[str] = None
    project_group_id: Optional[str] = None
    sidecar_type: Optional[str] = None
    scope_locked_at: Optional[float] = None
    approved_at: Optional[float] = None
    accepted_at: Optional[float] = None
    closed_at: Optional[float] = None
    lost_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "source": self.source,
            "customer_name": self.customer_name,
            "primary_lane": self.primary_lane,
            "status": self.status,
            "current_owner": self.current_owner,
            "next_action": self.next_action,
            "next_owner": self.next_owner,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "client_owner": self.client_owner,
            "pm_owner": self.pm_owner,
            "brian_exec": self.brian_exec,
            "brian_role": self.brian_role,
            "brand_or_system": self.brand_or_system,
            "raw_brief": self.raw_brief,
            "normalized_brief": self.normalized_brief,
            "budget_status": self.budget_status,
            "due_date": self.due_date,
            "executor": self.executor,
            "approver": self.approver,
            "quote_version": self.quote_version,
            "artifact_version": self.artifact_version,
            "notes": self.notes,
            "risk_flags": list(self.risk_flags),
            "parent_case_id": self.parent_case_id,
            "project_group_id": self.project_group_id,
            "sidecar_type": self.sidecar_type,
            "scope_locked_at": self.scope_locked_at,
            "approved_at": self.approved_at,
            "accepted_at": self.accepted_at,
            "closed_at": self.closed_at,
            "lost_reason": self.lost_reason,
        }
