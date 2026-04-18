#!/usr/bin/env python3
"""One-click live smoke check for project review / verify / escalate writeback."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


REQUIRED_EVENT_TYPES = [
    "escalation_raised",
    "verification_recorded",
    "artifact_written",
    "review_decided",
]


class SmokeCheckError(RuntimeError):
    pass


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmokeCheckError(f"HTTP {exc.code} for {method} {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SmokeCheckError(f"Request failed for {method} {url}: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SmokeCheckError(f"Non-JSON response for {method} {url}: {raw[:300]}") from exc


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeCheckError(message)


def run_smoke_check(
    *,
    base_url: str,
    title: str,
    phase_goal: str,
    next_action_summary: str,
    review_notes: str,
    verify_summary: str,
    escalation_reason: str,
    pause_autopilot: bool = True,
) -> dict[str, Any]:
    base_url = base_url.rstrip("/")
    create_payload = {
        "title": title,
        "phase_goal": phase_goal,
        "next_action_summary": next_action_summary,
    }
    project = request_json("POST", f"{base_url}/api/projects", create_payload)
    project_id = project["id"]

    if pause_autopilot:
        request_json("POST", f"{base_url}/api/projects/{project_id}/pause", {})

    review = request_json(
        "POST",
        f"{base_url}/api/projects/{project_id}/review",
        {"verdict": "PASS", "notes": review_notes},
    )
    verify = request_json(
        "POST",
        f"{base_url}/api/projects/{project_id}/verify",
        {"summary": verify_summary, "passed": True},
    )
    escalate = request_json(
        "POST",
        f"{base_url}/api/projects/{project_id}/escalate",
        {"reason": escalation_reason},
    )
    detail = request_json("GET", f"{base_url}/api/projects/{project_id}")

    latest_task = (detail.get("tasks") or [{}])[0]
    event_types = [event.get("event_type") for event in (detail.get("recent_events") or [])]
    verify_artifact = verify.get("artifact") or {}

    _assert((review.get("task") or {}).get("status") == "review_passed", "review did not set task.status=review_passed")
    _assert(verify_artifact.get("artifact_type") == "verification-report", "verify did not create verification-report artifact")
    _assert((escalate.get("project") or {}).get("status") == "blocked", "escalate did not return project.status=blocked")
    _assert(detail.get("status") == "blocked", "detail did not reflect blocked project status")
    _assert(detail.get("waiting_reason") == escalation_reason, "detail waiting_reason did not match escalation reason")
    _assert(latest_task.get("status") == "blocked", "latest task did not become blocked")
    _assert(latest_task.get("blocking_reason") == escalation_reason, "latest task blocking_reason did not match escalation reason")
    _assert(
        latest_task.get("output_artifact_id") == verify_artifact.get("id"),
        "latest task output_artifact_id did not match verification artifact id",
    )
    for required in REQUIRED_EVENT_TYPES:
        _assert(required in event_types, f"detail recent_events missing {required}")

    return {
        "ok": True,
        "base_url": base_url,
        "project_id": project_id,
        "review_task_status": (review.get("task") or {}).get("status"),
        "verify_artifact_id": verify_artifact.get("id"),
        "verify_artifact_type": verify_artifact.get("artifact_type"),
        "final_project_status": detail.get("status"),
        "final_waiting_reason": detail.get("waiting_reason"),
        "latest_task_status": latest_task.get("status"),
        "latest_task_blocking_reason": latest_task.get("blocking_reason"),
        "latest_task_output_artifact_id": latest_task.get("output_artifact_id"),
        "recent_event_types": event_types,
        "autopilot_paused_for_check": pause_autopilot,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a live review/verify/escalate writeback smoke check.")
    parser.add_argument("--base-url", default="http://127.0.0.1:9119", help="Hermes dashboard base URL")
    parser.add_argument("--title", default="Phase4 Writeback Live Check", help="Project title for the temporary live check")
    parser.add_argument(
        "--phase-goal",
        default="驗證 review / verify / escalation writeback live 生效",
        help="Phase goal written into the temporary project",
    )
    parser.add_argument(
        "--next-action-summary",
        default="先跑 review、verify、escalate 三段回寫，確認 live project detail 有反映。",
        help="Next action summary written into the temporary project",
    )
    parser.add_argument("--review-notes", default="spec 與品質都過", help="Review notes for the PASS writeback")
    parser.add_argument("--verify-summary", default="手動驗證通過", help="Verification summary for the verify writeback")
    parser.add_argument(
        "--escalation-reason",
        default="Phase4 live escalation：刻意標記 blocked 驗證 escalation writeback 可見。",
        help="Escalation reason for the blocker writeback",
    )
    parser.add_argument(
        "--no-pause-autopilot",
        action="store_true",
        help="Do not pause project autopilot before manual writeback checks",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_smoke_check(
            base_url=args.base_url,
            title=args.title,
            phase_goal=args.phase_goal,
            next_action_summary=args.next_action_summary,
            review_notes=args.review_notes,
            verify_summary=args.verify_summary,
            escalation_reason=args.escalation_reason,
            pause_autopilot=not args.no_pause_autopilot,
        )
    except SmokeCheckError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
