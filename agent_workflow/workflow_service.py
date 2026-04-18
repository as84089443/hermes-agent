from __future__ import annotations

from typing import Any, Optional

from .case_repository import CaseRepository
from .do_not_ask_detector import DoNotAskCandidateDetector
from .intake_service import IntakeService
from .message_intake_adapter import MessageIntakeAdapter
from .metrics import WorkflowMetricsAggregator
from .review_recap_writer import ReviewRecapWriter
from .routing_mismatch_tracker import RoutingMismatchTracker
from .routing_engine import RoutingEngine
from .sidecar_resolver import SidecarResolver


class WorkflowService:
    def __init__(
        self,
        repository: Optional[CaseRepository] = None,
        resolver: Optional[SidecarResolver] = None,
        routing_engine: Optional[RoutingEngine] = None,
        intake_service: Optional[IntakeService] = None,
        recap_writer: Optional[ReviewRecapWriter] = None,
        do_not_ask_detector: Optional[DoNotAskCandidateDetector] = None,
        mismatch_tracker: Optional[RoutingMismatchTracker] = None,
        metrics: Optional[WorkflowMetricsAggregator] = None,
    ):
        self.repository = repository or CaseRepository()
        self.resolver = resolver or SidecarResolver()
        self.routing_engine = routing_engine or RoutingEngine(self.resolver)
        self.intake_service = intake_service or IntakeService(self.repository, self.routing_engine)
        self.message_adapter = MessageIntakeAdapter()
        self.recap_writer = recap_writer or ReviewRecapWriter(self.resolver)
        self.do_not_ask_detector = do_not_ask_detector or DoNotAskCandidateDetector(self.resolver)
        self.mismatch_tracker = mismatch_tracker or RoutingMismatchTracker()
        self.metrics = metrics or WorkflowMetricsAggregator()
        self.metric_events: list[dict[str, Any]] = []
        self.mismatch_records: list[dict[str, Any]] = []
        self.recap_records: list[dict[str, Any]] = []

    def intake_message(
        self,
        *,
        message: str,
        source: str = "telegram",
        created_by: str = "Brian",
        draft_only: bool = False,
    ) -> dict[str, Any]:
        parsed = self.message_adapter.parse(message, source=source)
        result = self.intake_case(
            title=parsed["title"],
            source=parsed["source"],
            raw_brief=parsed["raw_brief"],
            customer_name=parsed.get("customer_name", ""),
            created_by=created_by,
            draft_only=draft_only,
        )
        return {
            "parsed_message": parsed,
            "workflow_result": result,
        }

    def close(self) -> None:
        self.repository.close()

    def intake_case(
        self,
        *,
        title: str,
        source: str,
        raw_brief: str,
        customer_name: str = "",
        created_by: str = "Brian",
        draft_only: bool = False,
    ) -> dict[str, Any]:
        if draft_only:
            draft = self.intake_service.build_case_draft(
                title=title,
                source=source,
                raw_brief=raw_brief,
                customer_name=customer_name,
                created_by=created_by,
            )
            self._append_clarification_events(draft["routing_result"])
            return draft

        case = self.intake_service.create_case_from_intake(
            title=title,
            source=source,
            raw_brief=raw_brief,
            customer_name=customer_name,
            created_by=created_by,
        )
        routing = self.routing_engine.route(title=title, customer_name=customer_name, raw_brief=raw_brief)
        self._append_clarification_events(routing)
        return {"case": case, "routing_result": routing}

    def record_routing_correction(
        self,
        *,
        case_id: str,
        final_values: dict[str, Any],
        human_explanation: str = "",
    ) -> dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case not found: {case_id}")
        routing_result = self.routing_engine.route(
            title=case.get("title", ""),
            customer_name=case.get("customer_name", ""),
            raw_brief=case.get("raw_brief", ""),
        )
        mismatch = self.mismatch_tracker.build_mismatch(
            case=case,
            routing_result=routing_result,
            final_values=final_values,
            human_explanation=human_explanation,
        )
        self.mismatch_records.append(mismatch)
        if mismatch.get("mismatched_fields"):
            self.metric_events.append(
                {
                    "event_type": "routing_mismatch_created",
                    "metric_family": "routing",
                    "value": 1,
                    "dimension": ",".join(mismatch["mismatched_fields"]),
                    "case_id": case_id,
                }
            )
        return mismatch

    def close_case_with_recap(
        self,
        *,
        case_id: str,
        recap_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case not found: {case_id}")
        recap = self.recap_writer.build_recap(case, recap_context or {})
        dna = self.do_not_ask_detector.detect(case=case, recap=recap)
        recap["do_not_ask_detector"] = dna
        self.recap_records.append(recap)
        self.metric_events.append(
            {
                "event_type": "recap_created",
                "metric_family": "closure",
                "value": 1,
                "dimension": case.get("primary_lane"),
                "case_id": case_id,
            }
        )
        if recap.get("pending_fields"):
            self.metric_events.append(
                {
                    "event_type": "recap_pending",
                    "metric_family": "closure",
                    "value": 1,
                    "dimension": ",".join(recap["pending_fields"]),
                    "case_id": case_id,
                }
            )
        if dna.get("candidate"):
            self.metric_events.append(
                {
                    "event_type": "do_not_ask_hit" if dna.get("confidence") == "high" else "do_not_ask_miss",
                    "metric_family": "learning",
                    "value": 1,
                    "dimension": case.get("title"),
                    "case_id": case_id,
                }
            )
        return recap

    def get_metrics_snapshot(self) -> dict[str, Any]:
        routed_cases = self.repository.list_cases(limit=1000)
        return self.metrics.build_snapshot(
            routed_cases=routed_cases,
            mismatches=self.mismatch_records,
            recap_records=self.recap_records,
            metric_events=self.metric_events,
        )

    def _append_clarification_events(self, routing_result: dict[str, Any]) -> None:
        for _question in routing_result.get("recommended_questions", []):
            self.metric_events.append(
                {
                    "event_type": "clarification_repeated",
                    "metric_family": "routing",
                    "value": 1,
                    "dimension": "question",
                }
            )
