from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from agent.memory_provider import MemoryProvider
from hermes_constants import display_hermes_home
from tools.registry import tool_error

from .extractor import LayeredMemoryExtractor
from .promotion import LayeredMemoryPromotion
from .retrieval import LayeredMemoryRetrieval
from .scopes import infer_memory_category, resolve_active_scope
from .store import LayeredMemoryStore


def _load_config(hermes_home: str | None = None) -> Dict[str, Any]:
    try:
        import yaml
    except Exception:
        return {}
    base = Path(hermes_home) if hermes_home else None
    if base is None:
        from hermes_constants import get_hermes_home
        base = get_hermes_home()
    config_path = base / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
    return (config.get("memory", {}) or {}).get("layered_memory", {}) or {}


class LayeredMemoryProvider(MemoryProvider):
    def __init__(self, config: Dict[str, Any] | None = None):
        self._config = config or {}
        self._store: LayeredMemoryStore | None = None
        self._retrieval: LayeredMemoryRetrieval | None = None
        self._extractor = LayeredMemoryExtractor()
        self._promotion = LayeredMemoryPromotion()
        self._session_id = ""
        self._active_scope = ("profile", "default")

    @property
    def name(self) -> str:
        return "layered_memory"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        hermes_home = kwargs.get("hermes_home")
        config = {**_load_config(hermes_home), **self._config}
        self._config = config
        db_path = config.get("db_path") or str(Path(hermes_home) / "layered_memory.db")
        self._store = LayeredMemoryStore(db_path)
        self._retrieval = LayeredMemoryRetrieval(self._store)
        self._session_id = session_id
        self._active_scope = resolve_active_scope(
            agent_identity=str(kwargs.get("agent_identity") or ""),
            user_id=str(kwargs.get("user_id") or ""),
            project_id=str(config.get("project_id") or kwargs.get("project_id") or ""),
        )

    def get_config_schema(self):
        default_db = f"{display_hermes_home()}/layered_memory.db"
        return [
            {"key": "db_path", "description": "SQLite database path for Layer 1 memory", "default": default_db},
            {"key": "project_id", "description": "Optional fixed project scope for this profile", "default": ""},
            {"key": "stale_candidate_days", "description": "Days before an unaccessed Layer 0 candidate is demoted back to working memory", "default": 30},
        ]

    def save_config(self, values, hermes_home):
        try:
            import yaml
        except Exception:
            return
        config_path = Path(hermes_home) / "config.yaml"
        existing = {}
        if config_path.exists():
            with open(config_path) as f:
                existing = yaml.safe_load(f) or {}
        existing.setdefault("memory", {})
        existing["memory"]["layered_memory"] = values
        with open(config_path, "w") as f:
            yaml.safe_dump(existing, f, default_flow_style=False, sort_keys=False)

    def _run_maintenance(self) -> None:
        if not self._store:
            return
        scope_type, scope_id = self._active_scope
        stale_days = int(self._config.get("stale_candidate_days") or 30)
        self._store.demote_stale_candidates(
            scope_type=scope_type,
            scope_id=scope_id,
            stale_days=stale_days,
        )

    def _build_status_payload(self) -> Dict[str, Any]:
        if not self._store:
            return {"success": False, "error": "Layered memory store is not initialized"}
        scope_type, scope_id = self._active_scope
        rows = self._store._conn.execute(
            """
            SELECT layer, state, COUNT(*) AS count
            FROM layered_memory_items
            WHERE scope_type = ? AND scope_id = ?
            GROUP BY layer, state
            """,
            (scope_type, scope_id),
        ).fetchall()
        counts: Dict[str, int] = {
            "total": 0,
            "confirmed": 0,
            "archive": 0,
            "working": 0,
            "stale": 0,
            "superseded": 0,
            "layer0_candidates": 0,
        }
        for row in rows:
            count = int(row["count"] or 0)
            counts["total"] += count
            counts[row["state"]] = counts.get(row["state"], 0) + count
            counts[row["layer"]] = counts.get(row["layer"], 0) + count
        counts["layer0_candidates"] = len(
            self._store.list_layer0_candidates(scope_type=scope_type, scope_id=scope_id, limit=20)
        )
        return {
            "success": True,
            "scope": {"type": scope_type, "id": scope_id},
            "counts": counts,
            "top_candidates": self._store.list_layer0_candidates(
                scope_type=scope_type,
                scope_id=scope_id,
                limit=5,
            ),
        }

    def system_prompt_block(self) -> str:
        if not self._store:
            return ""
        self._run_maintenance()
        scope_type, scope_id = self._active_scope
        candidates = self._store.list_layer0_candidates(scope_type=scope_type, scope_id=scope_id, limit=3)
        lines = [
            "# Layered Memory",
            f"Active scope: {scope_type}:{scope_id}",
            "Layer 1 handles retrieval-first working memory; Layer 2 holds archive/session evidence.",
        ]
        if candidates:
            lines.append("Layer 0 候選（待 canonical memory policy 決定是否升級）:")
            for row in candidates:
                lines.append(f"- [{row.get('category', 'memory')}] {row.get('abstract', '').strip()}")
        return "\n".join(lines)

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        if not self._retrieval or not self._retrieval.should_prefetch(query):
            return ""
        self._run_maintenance()
        scope_type, scope_id = self._active_scope
        rows = self._retrieval.search(query=query, scope_type=scope_type, scope_id=scope_id, limit=5)
        if not rows:
            rows = self._retrieval.search(
                query=query,
                scope_type=scope_type,
                scope_id=scope_id,
                limit=5,
                include_archive=True,
            )
        return self._retrieval.format_context(rows)

    def sync_turn(self, user_content: str, assistant_content: str, *, session_id: str = "") -> None:
        if not self._store:
            return None
        row = self._extractor.build_turn_memory_row(user_content, assistant_content)
        if not row:
            return None
        row = self._promotion.annotate_row(row, source="sync_turn")
        scope_type, scope_id = self._active_scope
        memory_id = self._store.upsert_memory(
            scope_type=scope_type,
            scope_id=scope_id,
            category=row["category"],
            abstract=row["abstract"],
            overview=row["overview"],
            content=row["content"],
            source="sync_turn",
            layer=row["layer"],
            tier=row["tier"],
            state=row["state"],
            confidence=row["confidence"],
            importance=row["importance"],
            metadata={**row.get("metadata", {}), "session_id": session_id or self._session_id},
        )
        if row.get("metadata", {}).get("layer0_candidate"):
            self._store.supersede_conflicting_memories(
                scope_type=scope_type,
                scope_id=scope_id,
                category=row["category"],
                keep_memory_id=memory_id,
                layer=row["layer"],
            )
        return None

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "layered_memory_list_candidates",
                "description": "List current Layer 0 promotion candidates from layered memory for the active scope.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of candidates to return.",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20,
                        }
                    },
                },
            },
            {
                "name": "layered_memory_search",
                "description": "Search layered memory rows for the active scope, optionally including archive/session evidence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query to run against layered memory."},
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return.",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20,
                        },
                        "include_archive": {
                            "type": "boolean",
                            "description": "Whether to include archive/session-summary rows in the search.",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "layered_memory_status",
                "description": "Summarize layered memory status for the active scope, including candidate and archive counts.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        if not self._store:
            return tool_error("Layered memory store is not initialized")
        self._run_maintenance()
        scope_type, scope_id = self._active_scope
        if tool_name == "layered_memory_list_candidates":
            limit = max(1, min(int(args.get("limit", 5) or 5), 20))
            candidates = self._store.list_layer0_candidates(
                scope_type=scope_type,
                scope_id=scope_id,
                limit=limit,
            )
            return json.dumps(
                {
                    "success": True,
                    "scope": {"type": scope_type, "id": scope_id},
                    "candidates": candidates,
                },
                ensure_ascii=False,
            )
        if tool_name == "layered_memory_search":
            query = str(args.get("query") or "").strip()
            if not query:
                return tool_error("query is required")
            limit = max(1, min(int(args.get("limit", 5) or 5), 20))
            include_archive = bool(args.get("include_archive", False))
            results = self._retrieval.search(
                query=query,
                scope_type=scope_type,
                scope_id=scope_id,
                limit=limit,
                include_archive=include_archive,
            ) if self._retrieval else []
            return json.dumps(
                {
                    "success": True,
                    "scope": {"type": scope_type, "id": scope_id},
                    "results": results,
                },
                ensure_ascii=False,
            )
        if tool_name == "layered_memory_status":
            return json.dumps(self._build_status_payload(), ensure_ascii=False)
        return tool_error(f"Provider {self.name} does not expose tool '{tool_name}'")

    def on_memory_write(self, action: str, target: str, content: str) -> None:
        if not self._store or action not in {"add", "replace"} or not content.strip():
            return
        scope_type, scope_id = self._active_scope
        category = infer_memory_category(target)
        self._store.upsert_memory(
            scope_type=scope_type,
            scope_id=scope_id,
            category=category,
            abstract=content.strip(),
            overview=content.strip(),
            content=content.strip(),
            source=f"builtin_memory:{target}:{action}",
            metadata={"layer0_candidate": True, "target": target, "action": action},
        )

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        if not self._store:
            return
        row = self._extractor.build_session_summary_row(messages)
        if not row:
            return
        scope_type, scope_id = self._active_scope
        self._store.upsert_memory(
            scope_type=scope_type,
            scope_id=scope_id,
            category=row["category"],
            abstract=row["abstract"],
            overview=row["overview"],
            content=row["content"],
            source="session_end",
            layer=row["layer"],
            tier=row["tier"],
            state=row["state"],
            confidence=row["confidence"],
            importance=row["importance"],
            metadata={**row.get("metadata", {}), "session_id": self._session_id},
        )

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        row = self._extractor.build_session_summary_row(messages)
        if not row:
            return ""
        return f"[Layered memory pre-compress summary]\n- {row['abstract']}\n- {row['overview']}"

    def shutdown(self) -> None:
        self._store = None
        self._retrieval = None
