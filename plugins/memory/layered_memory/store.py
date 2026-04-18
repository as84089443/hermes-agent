from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schema import SCHEMA_SQL
from .scopes import normalize_scope


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryRow:
    id: str
    scope_type: str
    scope_id: str
    category: str
    layer: str
    tier: str
    state: str
    abstract: str
    overview: str
    content: str
    source: str
    confidence: float
    importance: float
    access_count: int
    injection_count: int
    suppressed: int
    created_at: str
    updated_at: str
    last_accessed_at: Optional[str]
    metadata: Dict[str, Any]


class LayeredMemoryStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=10.0)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.executescript(SCHEMA_SQL)
            self._conn.commit()

    def upsert_memory(
        self,
        *,
        scope_type: str,
        scope_id: str,
        category: str,
        abstract: str,
        overview: str = "",
        content: str = "",
        source: str,
        layer: str = "working",
        tier: str = "working",
        state: str = "confirmed",
        confidence: float = 0.5,
        importance: float = 0.5,
        suppressed: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        scope_type, scope_id = normalize_scope(scope_type, scope_id)
        now = utc_now_iso()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)
        with self._lock:
            row = self._conn.execute(
                "SELECT id, created_at FROM layered_memory_items WHERE scope_type = ? AND scope_id = ? AND category = ? AND abstract = ?",
                (scope_type, scope_id, category, abstract.strip()),
            ).fetchone()
            if row:
                memory_id = row["id"]
                created_at = row["created_at"]
                self._conn.execute(
                    """
                    UPDATE layered_memory_items
                    SET overview = ?, content = ?, source = ?, layer = ?, tier = ?, state = ?,
                        confidence = ?, importance = ?, suppressed = ?, metadata_json = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        overview.strip(),
                        content.strip(),
                        source,
                        layer,
                        tier,
                        state,
                        confidence,
                        importance,
                        suppressed,
                        metadata_json,
                        now,
                        memory_id,
                    ),
                )
            else:
                memory_id = str(uuid.uuid4())
                created_at = now
                self._conn.execute(
                    """
                    INSERT INTO layered_memory_items (
                        id, scope_type, scope_id, category, layer, tier, state,
                        abstract, overview, content, source, confidence, importance,
                        suppressed, created_at, updated_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        memory_id,
                        scope_type,
                        scope_id,
                        category,
                        layer,
                        tier,
                        state,
                        abstract.strip(),
                        overview.strip(),
                        content.strip(),
                        source,
                        confidence,
                        importance,
                        suppressed,
                        created_at,
                        now,
                        metadata_json,
                    ),
                )
            self._conn.commit()
            return memory_id

    def query_memories(
        self,
        *,
        query: str,
        scope_type: str,
        scope_id: str,
        limit: int = 5,
        include_suppressed: bool = False,
        allowed_layers: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        scope_type, scope_id = normalize_scope(scope_type, scope_id)
        query = (query or "").strip()
        if not query:
            return []
        with self._lock:
            filters = ["m.scope_type = ?", "m.scope_id = ?", "m.state NOT IN ('archived', 'superseded')"]
            params: List[Any] = [scope_type, scope_id]
            if allowed_layers:
                placeholders = ",".join("?" for _ in allowed_layers)
                filters.append(f"m.layer IN ({placeholders})")
                params.extend(list(allowed_layers))
            if not include_suppressed:
                filters.append("m.suppressed = 0")
            where_clause = " AND ".join(filters)
            sql = f"""
                SELECT m.*
                FROM layered_memory_items m
                JOIN layered_memory_items_fts fts ON fts.rowid = m.rowid
                WHERE layered_memory_items_fts MATCH ?
                  AND {where_clause}
                ORDER BY bm25(layered_memory_items_fts), m.importance DESC, m.updated_at DESC
                LIMIT ?
            """
            rows = []
            try:
                rows = self._conn.execute(sql, [query, *params, limit]).fetchall()
            except sqlite3.OperationalError:
                rows = []
            if not rows:
                tokens = [part.strip() for part in query.split() if part.strip()]
                if not tokens:
                    tokens = [query]
                token_clause = " OR ".join(
                    "m.abstract LIKE ? OR m.overview LIKE ? OR m.content LIKE ?" for _ in tokens
                )
                fallback_sql = f"""
                    SELECT * FROM layered_memory_items m
                    WHERE {where_clause}
                      AND ({token_clause})
                    ORDER BY m.importance DESC, m.updated_at DESC
                    LIMIT ?
                """
                fallback_params: List[Any] = [*params]
                for token in tokens:
                    like = f"%{token}%"
                    fallback_params.extend([like, like, like])
                fallback_params.append(limit)
                rows = self._conn.execute(fallback_sql, fallback_params).fetchall()
            results = [self._row_to_dict(row) for row in rows]
            if results:
                self._apply_access_update([row["id"] for row in results])
            return results

    def list_layer0_candidates(self, *, scope_type: str, scope_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        scope_type, scope_id = normalize_scope(scope_type, scope_id)
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT *
                FROM layered_memory_items
                WHERE scope_type = ?
                  AND scope_id = ?
                  AND state = 'confirmed'
                  AND suppressed = 0
                  AND json_extract(metadata_json, '$.layer0_candidate') = 1
                ORDER BY importance DESC, confidence DESC, access_count DESC, updated_at DESC
                LIMIT ?
                """,
                (scope_type, scope_id, limit),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def supersede_conflicting_memories(
        self,
        *,
        scope_type: str,
        scope_id: str,
        category: str,
        keep_memory_id: str,
        layer: str = "working",
    ) -> None:
        scope_type, scope_id = normalize_scope(scope_type, scope_id)
        now = utc_now_iso()
        with self._lock:
            self._conn.execute(
                """
                UPDATE layered_memory_items
                SET state = 'superseded',
                    superseded_by_id = ?,
                    invalidated_at = ?,
                    updated_at = ?
                WHERE scope_type = ?
                  AND scope_id = ?
                  AND category = ?
                  AND layer = ?
                  AND id != ?
                  AND state NOT IN ('archived', 'superseded')
                  AND json_extract(metadata_json, '$.layer0_candidate') = 1
                """,
                (keep_memory_id, now, now, scope_type, scope_id, category, layer, keep_memory_id),
            )
            self._conn.commit()

    def demote_stale_candidates(
        self,
        *,
        scope_type: str,
        scope_id: str,
        stale_before: Optional[str] = None,
        stale_days: int = 30,
    ) -> int:
        scope_type, scope_id = normalize_scope(scope_type, scope_id)
        if stale_before is None:
            stale_before = (datetime.now(timezone.utc) - timedelta(days=stale_days)).isoformat()
        now = utc_now_iso()
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT id, importance, metadata_json
                FROM layered_memory_items
                WHERE scope_type = ?
                  AND scope_id = ?
                  AND state = 'confirmed'
                  AND tier = 'core_candidate'
                  AND suppressed = 0
                  AND json_extract(metadata_json, '$.layer0_candidate') = 1
                  AND COALESCE(last_accessed_at, updated_at, created_at) < ?
                  AND access_count <= 0
                """,
                (scope_type, scope_id, stale_before),
            ).fetchall()
            changed = 0
            for row in rows:
                metadata = json.loads(row["metadata_json"] or "{}")
                metadata["promotion_stage"] = "demoted_stale_candidate"
                metadata["demotion_reason"] = "stale_unaccessed_candidate"
                self._conn.execute(
                    """
                    UPDATE layered_memory_items
                    SET state = 'stale',
                        tier = 'working',
                        importance = ?,
                        metadata_json = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        max(float(row["importance"] or 0.0) - 0.25, 0.1),
                        json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                        now,
                        row["id"],
                    ),
                )
                changed += 1
            if changed:
                self._conn.commit()
            return changed

    def _apply_access_update(self, ids: List[str]) -> None:
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        self._conn.execute(
            f"UPDATE layered_memory_items SET access_count = access_count + 1, last_accessed_at = ? WHERE id IN ({placeholders})",
            [utc_now_iso(), *ids],
        )
        self._conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
        return data
