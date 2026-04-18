from __future__ import annotations

from typing import Any, Dict


class LayeredMemoryPromotion:
    """Conservative Layer 1 -> Layer 0 candidate evaluation.

    Phase-2 goal is not to auto-write Layer 0 yet, only to identify strong
    candidates so later promotion policy can consume them.
    """

    _DURABLE_TERMS = (
        "記得",
        "之後",
        "未來",
        "主路",
        "fork",
        "偏好",
        "不要再",
        "固定",
        "一律",
        "remember",
        "always",
        "default",
        "prefer",
        "from now on",
    )
    _PROMOTABLE_CATEGORIES = {"preference", "decision", "project", "identity"}

    def should_mark_layer0_candidate(self, row: Dict[str, Any]) -> bool:
        metadata = row.get("metadata") or {}
        if metadata.get("layer0_candidate"):
            return True

        category = str(row.get("category") or "")
        if category not in self._PROMOTABLE_CATEGORIES:
            return False

        combined_text = " ".join(
            str(row.get(field) or "") for field in ("abstract", "overview", "content")
        ).lower()
        if not any(term in combined_text for term in self._DURABLE_TERMS):
            return False

        confidence = float(row.get("confidence") or 0.0)
        importance = float(row.get("importance") or 0.0)
        return confidence >= 0.6 and importance >= 0.55

    def annotate_row(self, row: Dict[str, Any], *, source: str) -> Dict[str, Any]:
        updated = dict(row)
        metadata = dict(updated.get("metadata") or {})
        if self.should_mark_layer0_candidate(updated):
            metadata["layer0_candidate"] = True
            metadata.setdefault("promotion_stage", "candidate")
            metadata.setdefault("promotion_source", source)
            metadata.setdefault("promotion_reason", "durable_preference_or_decision")
            updated["tier"] = "core_candidate"
            updated["importance"] = max(float(updated.get("importance") or 0.0), 0.75)
            updated["confidence"] = max(float(updated.get("confidence") or 0.0), 0.75)
        updated["metadata"] = metadata
        return updated
