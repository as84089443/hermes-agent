"""Persistent project runtime ledger for Hermes web/dashboard control.

This is a lightweight SQLite-backed control plane for project progression.
It intentionally complements SessionDB instead of replacing it.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_constants import get_hermes_home

_DB_PATH = get_hermes_home() / "project_runtime.db"
_DB_LOCK = threading.Lock()


def _utc_now() -> float:
    return time.time()


class ProjectStateDB:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or _DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._ensure_schema()

    def close(self) -> None:
        self.conn.close()

    def _ensure_schema(self) -> None:
        with _DB_LOCK:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    main_phase TEXT,
                    phase_goal TEXT,
                    phase_artifact_target TEXT,
                    phase_verification_target TEXT,
                    current_owner TEXT,
                    next_action_type TEXT,
                    next_action_summary TEXT,
                    next_action_payload_json TEXT,
                    autopilot_enabled INTEGER NOT NULL DEFAULT 1,
                    waiting_reason TEXT,
                    session_id TEXT,
                    last_cycle_at REAL,
                    last_cycle_status TEXT,
                    last_cycle_summary TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    task_type TEXT,
                    status TEXT NOT NULL,
                    owner_role TEXT,
                    join_owner TEXT,
                    input_artifact_ids_json TEXT,
                    output_artifact_id TEXT,
                    blocking_reason TEXT,
                    child_session_id TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL,
                    title TEXT,
                    path TEXT,
                    checksum TEXT,
                    produced_by_task_id TEXT,
                    supersedes_artifact_id TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    gate TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    artifact_refs_json TEXT,
                    status TEXT NOT NULL,
                    requested_by TEXT,
                    decided_by TEXT,
                    decision_notes TEXT,
                    requested_at REAL NOT NULL,
                    decided_at REAL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id TEXT,
                    payload_json TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_approvals_project_status ON approvals(project_id, status, requested_at DESC);
                CREATE INDEX IF NOT EXISTS idx_events_project_created_at ON events(project_id, created_at DESC);
                """
            )
            self.conn.commit()

    def _row_to_dict(self, row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        if row is None:
            return None
        return dict(row)

    def _json_load(self, value: Optional[str], fallback: Any) -> Any:
        if not value:
            return fallback
        try:
            return json.loads(value)
        except Exception:
            return fallback

    def _project_summary(self, row: sqlite3.Row) -> Dict[str, Any]:
        project_id = row["id"]
        pending_approvals = self.conn.execute(
            "SELECT COUNT(*) FROM approvals WHERE project_id = ? AND status = 'pending'",
            (project_id,),
        ).fetchone()[0]
        open_tasks = self.conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status NOT IN ('done', 'cancelled')",
            (project_id,),
        ).fetchone()[0]
        return {
            **dict(row),
            "autopilot_enabled": bool(row["autopilot_enabled"]),
            "open_approvals": pending_approvals,
            "open_tasks": open_tasks,
        }

    def create_project(
        self,
        *,
        title: str,
        phase_goal: Optional[str] = None,
        main_phase: str = "需求整理",
        next_action_type: str = "execute_task",
        next_action_summary: Optional[str] = None,
        current_owner: str = "Hermes 公司系統",
    ) -> Dict[str, Any]:
        now = _utc_now()
        project_id = f"proj_{int(now)}_{secrets.token_hex(4)}"
        next_summary = (next_action_summary or "整理需求、建立主 phase，然後把下一步推進到可執行狀態。")[:400]
        with _DB_LOCK:
            self.conn.execute(
                """
                INSERT INTO projects (
                    id, title, status, main_phase, phase_goal,
                    phase_artifact_target, phase_verification_target,
                    current_owner, next_action_type, next_action_summary,
                    next_action_payload_json, autopilot_enabled, waiting_reason,
                    session_id, last_cycle_at, last_cycle_status, last_cycle_summary,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    title.strip(),
                    "in_progress",
                    main_phase,
                    phase_goal,
                    "可檢查的專案產物",
                    "至少完成一輪可見驗證",
                    current_owner,
                    next_action_type,
                    next_summary,
                    json.dumps({}, ensure_ascii=False),
                    1,
                    None,
                    None,
                    None,
                    None,
                    None,
                    now,
                    now,
                ),
            )
            self.conn.execute(
                """
                INSERT INTO tasks (
                    id, project_id, title, task_type, status, owner_role,
                    join_owner, input_artifact_ids_json, output_artifact_id,
                    blocking_reason, child_session_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"task_{secrets.token_hex(4)}",
                    project_id,
                    next_summary,
                    "orchestrator",
                    "queued",
                    current_owner,
                    current_owner,
                    json.dumps([], ensure_ascii=False),
                    None,
                    None,
                    None,
                    now,
                    now,
                ),
            )
            self.conn.execute(
                "INSERT INTO events (project_id, event_type, entity_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    project_id,
                    "project_created",
                    "project",
                    project_id,
                    json.dumps({"summary": f"已建立專案：{title.strip()}"}, ensure_ascii=False),
                    now,
                ),
            )
            self.conn.commit()
        return self.get_project(project_id)

    def list_projects(self, *, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._project_summary(row) for row in rows]

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            return None
        project = self._project_summary(row)
        task_rows = self.conn.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY updated_at DESC",
            (project_id,),
        ).fetchall()
        approval_rows = self.conn.execute(
            "SELECT * FROM approvals WHERE project_id = ? ORDER BY requested_at DESC",
            (project_id,),
        ).fetchall()
        event_rows = self.conn.execute(
            "SELECT * FROM events WHERE project_id = ? ORDER BY created_at DESC LIMIT 30",
            (project_id,),
        ).fetchall()
        project["tasks"] = [
            {
                **dict(row),
                "input_artifact_ids": self._json_load(row["input_artifact_ids_json"], []),
            }
            for row in task_rows
        ]
        project["approvals"] = [
            {
                **dict(row),
                "artifact_refs": self._json_load(row["artifact_refs_json"], []),
            }
            for row in approval_rows
        ]
        project["recent_events"] = [
            {
                **dict(row),
                "payload": self._json_load(row["payload_json"], {}),
                "summary": self._json_load(row["payload_json"], {}).get("summary") or row["event_type"],
            }
            for row in event_rows
        ]
        return project

    def list_approvals(self, *, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if status:
            rows = self.conn.execute(
                "SELECT * FROM approvals WHERE status = ? ORDER BY requested_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM approvals ORDER BY requested_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                **dict(row),
                "artifact_refs": self._json_load(row["artifact_refs_json"], []),
            }
            for row in rows
        ]

    def append_event(
        self,
        *,
        project_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "INSERT INTO events (project_id, event_type, entity_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    project_id,
                    event_type,
                    entity_type,
                    entity_id,
                    json.dumps(payload or {}, ensure_ascii=False),
                    now,
                ),
            )
            self.conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
            self.conn.commit()

    def set_autopilot(self, project_id: str, enabled: bool) -> Optional[Dict[str, Any]]:
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE projects SET autopilot_enabled = ?, updated_at = ? WHERE id = ?",
                (1 if enabled else 0, now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="autopilot_resumed" if enabled else "autopilot_paused",
            entity_type="project",
            entity_id=project_id,
            payload={"summary": "已恢復自動推進" if enabled else "已暫停自動推進"},
        )
        return self.get_project(project_id)

    def create_approval(
        self,
        *,
        project_id: str,
        gate: str,
        title: str,
        summary: str,
        requested_by: str = "Hermes",
        artifact_refs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        approval_id = f"approval_{secrets.token_hex(4)}"
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                """
                INSERT INTO approvals (
                    id, project_id, gate, title, summary, artifact_refs_json,
                    status, requested_by, decided_by, decision_notes, requested_at, decided_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    project_id,
                    gate,
                    title,
                    summary,
                    json.dumps(artifact_refs or [], ensure_ascii=False),
                    "pending",
                    requested_by,
                    None,
                    None,
                    now,
                    None,
                ),
            )
            self.conn.execute(
                "UPDATE projects SET status = ?, waiting_reason = ?, updated_at = ? WHERE id = ?",
                ("waiting_on_human", summary[:400], now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="approval_requested",
            entity_type="approval",
            entity_id=approval_id,
            payload={"summary": title, "gate": gate},
        )
        approval = self.conn.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        return {
            **dict(approval),
            "artifact_refs": self._json_load(approval["artifact_refs_json"], []),
        }

    def _latest_task_row(self, project_id: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY updated_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()

    def write_artifact(
        self,
        *,
        project_id: str,
        artifact_type: str,
        title: str,
        status: str = "final",
        path: Optional[str] = None,
        checksum: Optional[str] = None,
        produced_by_task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = _utc_now()
        latest = self.conn.execute(
            "SELECT MAX(version) FROM artifacts WHERE project_id = ? AND artifact_type = ?",
            (project_id, artifact_type),
        ).fetchone()[0]
        version = int(latest or 0) + 1
        artifact_id = f"artifact_{secrets.token_hex(4)}"
        with _DB_LOCK:
            self.conn.execute(
                """
                INSERT INTO artifacts (
                    id, project_id, artifact_type, version, status, title,
                    path, checksum, produced_by_task_id, supersedes_artifact_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    project_id,
                    artifact_type,
                    version,
                    status,
                    title,
                    path,
                    checksum,
                    produced_by_task_id,
                    None,
                    now,
                ),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="artifact_written",
            entity_type="artifact",
            entity_id=artifact_id,
            payload={"summary": title, "artifact_type": artifact_type, "version": version},
        )
        return dict(self.conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone())

    def complete_latest_task(
        self,
        *,
        project_id: str,
        summary: str,
        output_artifact_id: Optional[str] = None,
        child_session_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        row = self._latest_task_row(project_id)
        if row is None:
            return None
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE tasks SET status = ?, output_artifact_id = COALESCE(?, output_artifact_id), child_session_id = COALESCE(?, child_session_id), updated_at = ? WHERE id = ?",
                ("done", output_artifact_id, child_session_id, now, row["id"]),
            )
            self.conn.execute(
                "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
                ("in_progress", now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="task_state_changed",
            entity_type="task",
            entity_id=row["id"],
            payload={"summary": summary, "status": "done"},
        )
        return dict(self.conn.execute("SELECT * FROM tasks WHERE id = ?", (row["id"],)).fetchone())

    def record_review_verdict(
        self,
        *,
        project_id: str,
        verdict: str,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        row = self._latest_task_row(project_id)
        if row is None:
            return None
        normalized = verdict.strip().upper()
        next_status = "review_passed" if normalized == "PASS" else "needs_revision"
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (next_status, now, row["id"]),
            )
            self.conn.execute(
                "UPDATE projects SET status = ?, waiting_reason = ?, updated_at = ? WHERE id = ?",
                ("in_progress" if normalized == "PASS" else "needs_revision", None if normalized == "PASS" else notes, now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="review_decided",
            entity_type="task",
            entity_id=row["id"],
            payload={"summary": f"Review verdict：{normalized}", "notes": notes},
        )
        return dict(self.conn.execute("SELECT * FROM tasks WHERE id = ?", (row["id"],)).fetchone())

    def record_verification(
        self,
        *,
        project_id: str,
        summary: str,
        passed: bool,
    ) -> Optional[Dict[str, Any]]:
        latest_task = self._latest_task_row(project_id)
        artifact = self.write_artifact(
            project_id=project_id,
            artifact_type="verification-report",
            title=summary,
            status="final" if passed else "draft",
            produced_by_task_id=latest_task["id"] if latest_task is not None else None,
        )
        if latest_task is None:
            return artifact
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE tasks SET status = ?, output_artifact_id = ?, updated_at = ? WHERE id = ?",
                ("verified" if passed else "needs_revision", artifact.get("id"), now, latest_task["id"]),
            )
            self.conn.execute(
                "UPDATE projects SET status = ?, waiting_reason = ?, updated_at = ? WHERE id = ?",
                ("in_progress" if passed else "needs_revision", None if passed else summary, now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="verification_recorded",
            entity_type="task",
            entity_id=latest_task["id"],
            payload={"summary": summary, "passed": passed, "artifact_id": artifact.get("id")},
        )
        return artifact

    def escalate_blocker(self, *, project_id: str, reason: str) -> Optional[Dict[str, Any]]:
        row = self._latest_task_row(project_id)
        now = _utc_now()
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE projects SET status = ?, waiting_reason = ?, updated_at = ? WHERE id = ?",
                ("blocked", reason[:1000], now, project_id),
            )
            if row is not None:
                self.conn.execute(
                    "UPDATE tasks SET status = ?, blocking_reason = ?, updated_at = ? WHERE id = ?",
                    ("blocked", reason[:1000], now, row["id"]),
                )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="escalation_raised",
            entity_type="task" if row is not None else "project",
            entity_id=row["id"] if row is not None else project_id,
            payload={"summary": reason[:400]},
        )
        return self.get_project(project_id)

    def decide_approval(
        self,
        *,
        approval_id: str,
        decision: str,
        notes: Optional[str] = None,
        decided_by: str = "operator",
    ) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        if row is None:
            return None
        project_id = row["project_id"]
        normalized = {
            "approve": "approved",
            "approved": "approved",
            "changes_requested": "changes_requested",
            "revise": "changes_requested",
            "reject": "rejected",
            "rejected": "rejected",
        }.get(decision, decision)
        now = _utc_now()
        project_status = "in_progress" if normalized == "approved" else "needs_revision"
        waiting_reason = None if normalized == "approved" else (notes or row["summary"])
        with _DB_LOCK:
            self.conn.execute(
                "UPDATE approvals SET status = ?, decided_by = ?, decision_notes = ?, decided_at = ? WHERE id = ?",
                (normalized, decided_by, notes, now, approval_id),
            )
            self.conn.execute(
                "UPDATE projects SET status = ?, waiting_reason = ?, updated_at = ? WHERE id = ?",
                (project_status, waiting_reason, now, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="approval_decided",
            entity_type="approval",
            entity_id=approval_id,
            payload={"summary": f"審批結果：{normalized}", "decision_notes": notes},
        )
        updated = self.conn.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        return {
            **dict(updated),
            "artifact_refs": self._json_load(updated["artifact_refs_json"], []),
        }

    def record_project_push(
        self,
        *,
        project_id: str,
        summary: str,
        session_id: str,
        status: str = "executed",
        next_action_summary: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        now = _utc_now()
        normalized_session_id = session_id or None
        with _DB_LOCK:
            self.conn.execute(
                """
                UPDATE projects
                SET session_id = COALESCE(?, session_id),
                    last_cycle_at = ?,
                    last_cycle_status = ?,
                    last_cycle_summary = ?,
                    status = ?,
                    waiting_reason = CASE WHEN ? = 'executed' THEN NULL ELSE waiting_reason END,
                    next_action_summary = COALESCE(?, next_action_summary),
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    normalized_session_id,
                    now,
                    status,
                    summary[:1000],
                    "in_progress" if status == "executed" else status,
                    status,
                    next_action_summary,
                    now,
                    project_id,
                ),
            )
            self.conn.execute(
                """
                UPDATE tasks
                SET status = ?, child_session_id = COALESCE(?, child_session_id), updated_at = ?
                WHERE project_id = ? AND id = (
                    SELECT id FROM tasks WHERE project_id = ? ORDER BY updated_at DESC LIMIT 1
                )
                """,
                ("in_progress" if status in {"running", "executed"} else status, normalized_session_id, now, project_id, project_id),
            )
            self.conn.commit()
        self.append_event(
            project_id=project_id,
            event_type="project_pushed",
            entity_type="project",
            entity_id=project_id,
            payload={"summary": summary[:400], "session_id": normalized_session_id, "status": status},
        )
        return self.get_project(project_id)
