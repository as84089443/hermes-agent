from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Optional

from hermes_constants import get_hermes_home

_DB_PATH = get_hermes_home() / "workflow_cases.db"
_DB_LOCK = threading.Lock()


class WorkflowStorage:
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
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    primary_lane TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_owner TEXT NOT NULL,
                    next_action TEXT NOT NULL,
                    next_owner TEXT NOT NULL,
                    client_owner TEXT,
                    pm_owner TEXT,
                    brian_exec TEXT,
                    brian_role TEXT,
                    brand_or_system TEXT,
                    raw_brief TEXT,
                    normalized_brief TEXT,
                    budget_status TEXT,
                    due_date TEXT,
                    executor TEXT,
                    approver TEXT,
                    quote_version TEXT,
                    artifact_version TEXT,
                    notes TEXT,
                    risk_flags_json TEXT,
                    parent_case_id TEXT,
                    project_group_id TEXT,
                    sidecar_type TEXT,
                    scope_locked_at REAL,
                    approved_at REAL,
                    accepted_at REAL,
                    closed_at REAL,
                    lost_reason TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workflow_cases_status ON cases(status);
                CREATE INDEX IF NOT EXISTS idx_workflow_cases_lane ON cases(primary_lane);
                CREATE INDEX IF NOT EXISTS idx_workflow_cases_owner ON cases(current_owner);
                CREATE INDEX IF NOT EXISTS idx_workflow_cases_updated_at ON cases(updated_at DESC);
                """
            )
            self.conn.commit()
