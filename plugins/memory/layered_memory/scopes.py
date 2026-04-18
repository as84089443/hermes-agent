from __future__ import annotations

from typing import Optional, Tuple


def resolve_active_scope(*, agent_identity: str = "", user_id: str = "", project_id: str = "") -> Tuple[str, str]:
    if project_id:
        return ("project", project_id)
    if user_id:
        return ("user", user_id)
    if agent_identity:
        return ("profile", agent_identity)
    return ("profile", "default")


def infer_memory_category(target: str) -> str:
    if target == "user":
        return "preference"
    return "environment"


def normalize_scope(scope_type: Optional[str], scope_id: Optional[str]) -> Tuple[str, str]:
    return ((scope_type or "profile").strip() or "profile", (scope_id or "default").strip() or "default")
