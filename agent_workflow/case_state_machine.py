from __future__ import annotations

from .case_validation import CaseValidationError

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "intake": {"clarifying", "ready_for_quote", "lost"},
    "clarifying": {"ready_for_quote", "lost"},
    "ready_for_quote": {"quote_sent", "soft_hold", "confirmed", "lost"},
    "quote_sent": {"quote_sent", "soft_hold", "confirmed", "lost"},
    "soft_hold": {"confirmed", "quote_sent", "lost"},
    "confirmed": {"in_execution", "lost"},
    "in_execution": {"delivered"},
    "delivered": {"billing", "collected", "closed"},
    "billing": {"collected", "closed"},
    "collected": {"closed"},
    "closed": set(),
    "lost": set(),
}


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())


def ensure_valid_transition(from_status: str, to_status: str) -> None:
    if not can_transition(from_status, to_status):
        allowed = sorted(ALLOWED_TRANSITIONS.get(from_status, set()))
        raise CaseValidationError(
            f"Illegal status transition: {from_status!r} -> {to_status!r}. Allowed: {allowed}"
        )
