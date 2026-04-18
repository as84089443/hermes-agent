from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WorkflowMetricsSnapshot:
    routing_correction_rate: float
    repeated_clarification_count: int
    do_not_ask_hit_rate: float
    recap_pending_rate: float
    routing_case_count: int
    mismatch_count: int
    do_not_ask_hit_count: int
    do_not_ask_total_count: int
    recap_count: int
    recap_pending_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "routing_correction_rate": self.routing_correction_rate,
            "repeated_clarification_count": self.repeated_clarification_count,
            "do_not_ask_hit_rate": self.do_not_ask_hit_rate,
            "recap_pending_rate": self.recap_pending_rate,
            "routing_case_count": self.routing_case_count,
            "mismatch_count": self.mismatch_count,
            "do_not_ask_hit_count": self.do_not_ask_hit_count,
            "do_not_ask_total_count": self.do_not_ask_total_count,
            "recap_count": self.recap_count,
            "recap_pending_count": self.recap_pending_count,
        }


class WorkflowMetricsAggregator:
    def build_snapshot(
        self,
        *,
        routed_cases: list[dict[str, Any]],
        mismatches: list[dict[str, Any]],
        recap_records: list[dict[str, Any]],
        metric_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        metric_events = metric_events or []

        routing_case_count = len(routed_cases)
        mismatch_count = len([m for m in mismatches if m.get("mismatched_fields")])
        routing_correction_rate = mismatch_count / routing_case_count if routing_case_count else 0.0

        repeated_clarification_count = sum(
            1 for event in metric_events if event.get("event_type") == "clarification_repeated"
        )

        do_not_ask_total_count = sum(
            1
            for event in metric_events
            if event.get("event_type") in {"do_not_ask_hit", "do_not_ask_miss"}
        )
        do_not_ask_hit_count = sum(
            1 for event in metric_events if event.get("event_type") == "do_not_ask_hit"
        )
        do_not_ask_hit_rate = (
            do_not_ask_hit_count / do_not_ask_total_count if do_not_ask_total_count else 0.0
        )

        recap_count = len(recap_records)
        recap_pending_count = sum(1 for recap in recap_records if recap.get("pending_fields"))
        recap_pending_rate = recap_pending_count / recap_count if recap_count else 0.0

        snapshot = WorkflowMetricsSnapshot(
            routing_correction_rate=routing_correction_rate,
            repeated_clarification_count=repeated_clarification_count,
            do_not_ask_hit_rate=do_not_ask_hit_rate,
            recap_pending_rate=recap_pending_rate,
            routing_case_count=routing_case_count,
            mismatch_count=mismatch_count,
            do_not_ask_hit_count=do_not_ask_hit_count,
            do_not_ask_total_count=do_not_ask_total_count,
            recap_count=recap_count,
            recap_pending_count=recap_pending_count,
        )
        return snapshot.to_dict()
