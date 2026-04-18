from __future__ import annotations

from typing import Dict, List


def _clean_message_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text") or "").strip())
        return " ".join(part for part in parts if part).strip()
    return ""


class LayeredMemoryExtractor:
    """Minimal extraction helpers for Layer 1/Layer 2 bootstrap.

    MVP policy is intentionally conservative:
    - build compact session summaries for archive writes
    - extract at most one working-memory row per turn when the user message
      shows continuity or durable preference/decision intent
    """

    def extract_candidates(self, messages: List[Dict]) -> List[Dict]:
        return []

    def build_turn_memory_row(self, user_content: str, assistant_content: str) -> Dict | None:
        user_text = _clean_message_content(user_content)
        assistant_text = _clean_message_content(assistant_content)
        if not user_text:
            return None

        lowered = user_text.lower()
        continuity_terms = (
            "記得", "之後", "未來", "主路", "fork", "偏好", "不要再", "固定", "一律",
            "remember", "always", "default", "prefer", "from now on", "use fork",
        )
        if not any(term in lowered for term in continuity_terms):
            return None

        abstract = user_text[:200]
        overview_parts = [f"User durable cue: {user_text[:160]}"]
        if assistant_text:
            overview_parts.append(f"Assistant response: {assistant_text[:160]}")
        overview = " | ".join(overview_parts)[:400]
        content = "\n".join(part for part in [f"[user] {user_text}", f"[assistant] {assistant_text}" if assistant_text else ""] if part)[:4000]

        category = "preference"
        if any(term in lowered for term in ("fork", "主路", "project", "repo")):
            category = "decision"

        return {
            "category": category,
            "abstract": abstract,
            "overview": overview,
            "content": content,
            "layer": "working",
            "tier": "working",
            "state": "confirmed",
            "confidence": 0.65,
            "importance": 0.6,
            "metadata": {"summary_kind": "sync_turn"},
        }

    def build_session_summary_row(self, messages: List[Dict]) -> Dict | None:
        cleaned = []
        for msg in messages:
            role = msg.get("role")
            if role not in {"user", "assistant"}:
                continue
            text = _clean_message_content(msg.get("content"))
            if not text:
                continue
            cleaned.append((role, text))
        if not cleaned:
            return None

        recent = cleaned[-6:]
        user_lines = [text for role, text in recent if role == "user"]
        assistant_lines = [text for role, text in recent if role == "assistant"]
        abstract = user_lines[-1] if user_lines else recent[-1][1]
        overview_parts = []
        if user_lines:
            overview_parts.append(f"User focus: {user_lines[-1][:160]}")
        if assistant_lines:
            overview_parts.append(f"Latest assistant outcome: {assistant_lines[-1][:160]}")
        overview = " | ".join(overview_parts)[:400]
        content = "\n".join(f"[{role}] {text}" for role, text in recent)[:4000]
        return {
            "category": "session-summary",
            "abstract": abstract[:200],
            "overview": overview,
            "content": content,
            "layer": "archive",
            "tier": "peripheral",
            "state": "confirmed",
            "confidence": 0.6,
            "importance": 0.4,
            "metadata": {"summary_kind": "session_end", "message_count": len(recent)},
        }
