from __future__ import annotations

from typing import Dict, List


_CONTINUITY_TERMS = (
    "上次", "之前", "剛剛", "延續", "繼續", "記得", "回來", "這條路", "同一個",
    "last time", "previously", "continue", "remember", "same repo", "same project",
)


class LayeredMemoryRetrieval:
    def __init__(self, store):
        self.store = store

    def should_prefetch(self, query: str) -> bool:
        text = (query or "").strip().lower()
        if not text:
            return False
        if len(text) <= 2:
            return False
        if any(term in text for term in _CONTINUITY_TERMS):
            return True
        if "?" in text or "？" in text:
            return True
        return len(text.split()) >= 4

    def search(self, *, query: str, scope_type: str, scope_id: str, limit: int = 5, include_archive: bool = False) -> List[Dict]:
        return self.store.query_memories(
            query=query,
            scope_type=scope_type,
            scope_id=scope_id,
            limit=limit,
            allowed_layers=["working", "durable", "reflection", "archive"] if include_archive else ["working", "durable", "reflection"],
        )

    def format_context(self, rows: List[Dict]) -> str:
        if not rows:
            return ""
        lines = ["## Layered Working Memory"]
        for row in rows:
            prefix = row.get("category", "memory")
            abstract = row.get("abstract", "").strip()
            if abstract:
                lines.append(f"- [{prefix}] {abstract}")
        return "\n".join(lines)
