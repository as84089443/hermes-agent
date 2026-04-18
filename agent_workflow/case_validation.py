from __future__ import annotations

from typing import Any, Mapping

from .case_models import (
    BRIAN_EXEC_VALUES,
    BRIAN_ROLE_VALUES,
    BUDGET_STATUS_VALUES,
    CLIENT_OWNER_VALUES,
    IMMUTABLE_FIELDS,
    PM_OWNER_VALUES,
    PRIMARY_LANE_VALUES,
    REQUIRED_FIELDS,
    SIDECAR_TYPE_VALUES,
    STATUS_VALUES,
)


class CaseValidationError(ValueError):
    """Raised when a case payload is invalid."""


def _require_non_empty_string(payload: Mapping[str, Any], field: str) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CaseValidationError(f"Field '{field}' is required and must be a non-empty string")


def _validate_enum(payload: Mapping[str, Any], field: str, allowed: tuple[str, ...]) -> None:
    value = payload.get(field)
    if value is None:
        return
    if value not in allowed:
        raise CaseValidationError(f"Field '{field}' must be one of {allowed}, got {value!r}")


def validate_create_payload(payload: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field in ("created_at", "updated_at"):
            if payload.get(field) is None:
                raise CaseValidationError(f"Field '{field}' is required")
            continue
        _require_non_empty_string(payload, field)

    if not isinstance(payload.get("created_at"), (int, float)):
        raise CaseValidationError("Field 'created_at' must be a timestamp")
    if not isinstance(payload.get("updated_at"), (int, float)):
        raise CaseValidationError("Field 'updated_at' must be a timestamp")

    _validate_common_fields(payload)


def validate_update_patch(patch: Mapping[str, Any]) -> None:
    if not patch:
        raise CaseValidationError("Update patch cannot be empty")
    for field in patch:
        if field in IMMUTABLE_FIELDS:
            raise CaseValidationError(f"Field '{field}' is immutable")
        if field == "status":
            raise CaseValidationError("Field 'status' must be changed via transition_case")
    _validate_common_fields(patch)


def _validate_common_fields(payload: Mapping[str, Any]) -> None:
    _validate_enum(payload, "client_owner", CLIENT_OWNER_VALUES)
    _validate_enum(payload, "pm_owner", PM_OWNER_VALUES)
    _validate_enum(payload, "brian_exec", BRIAN_EXEC_VALUES)
    _validate_enum(payload, "brian_role", BRIAN_ROLE_VALUES)
    _validate_enum(payload, "primary_lane", PRIMARY_LANE_VALUES)
    _validate_enum(payload, "status", STATUS_VALUES)
    _validate_enum(payload, "budget_status", BUDGET_STATUS_VALUES)
    _validate_enum(payload, "sidecar_type", SIDECAR_TYPE_VALUES)

    if "risk_flags" in payload and payload["risk_flags"] is not None:
        if not isinstance(payload["risk_flags"], list) or not all(isinstance(x, str) for x in payload["risk_flags"]):
            raise CaseValidationError("Field 'risk_flags' must be a list of strings")
