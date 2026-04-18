from __future__ import annotations

from agent_workflow.metrics import WorkflowMetricsAggregator


def test_metrics_aggregator_computes_core_rates():
    agg = WorkflowMetricsAggregator()
    routed_cases = [
        {"case_id": "c1"},
        {"case_id": "c2"},
        {"case_id": "c3"},
        {"case_id": "c4"},
    ]
    mismatches = [
        {"case_id": "c1", "mismatched_fields": ["client_owner"]},
        {"case_id": "c3", "mismatched_fields": ["brian_exec"]},
    ]
    recap_records = [
        {"case_id": "c1", "pending_fields": []},
        {"case_id": "c2", "pending_fields": ["pm_owner_final"]},
        {"case_id": "c3", "pending_fields": []},
    ]
    metric_events = [
        {"event_type": "clarification_repeated"},
        {"event_type": "clarification_repeated"},
        {"event_type": "do_not_ask_hit"},
        {"event_type": "do_not_ask_hit"},
        {"event_type": "do_not_ask_miss"},
    ]

    snapshot = agg.build_snapshot(
        routed_cases=routed_cases,
        mismatches=mismatches,
        recap_records=recap_records,
        metric_events=metric_events,
    )

    assert snapshot["routing_case_count"] == 4
    assert snapshot["mismatch_count"] == 2
    assert snapshot["routing_correction_rate"] == 0.5
    assert snapshot["repeated_clarification_count"] == 2
    assert snapshot["do_not_ask_hit_count"] == 2
    assert snapshot["do_not_ask_total_count"] == 3
    assert snapshot["do_not_ask_hit_rate"] == 2 / 3
    assert snapshot["recap_count"] == 3
    assert snapshot["recap_pending_count"] == 1
    assert snapshot["recap_pending_rate"] == 1 / 3



def test_metrics_aggregator_handles_empty_inputs():
    agg = WorkflowMetricsAggregator()
    snapshot = agg.build_snapshot(routed_cases=[], mismatches=[], recap_records=[], metric_events=[])

    assert snapshot["routing_correction_rate"] == 0.0
    assert snapshot["repeated_clarification_count"] == 0
    assert snapshot["do_not_ask_hit_rate"] == 0.0
    assert snapshot["recap_pending_rate"] == 0.0
