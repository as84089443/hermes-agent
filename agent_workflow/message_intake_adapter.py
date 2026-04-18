from __future__ import annotations

import re
from typing import Any


class MessageIntakeAdapter:
    """Convert a free-form message into intake service inputs.

    v1 supports two styles:
    1. Semi-structured lines like:
       客戶：碼非
       案名：中堅企業獎拍攝
       類型：企業活動拍攝
       日期/交期：10/07
       Brian出工：是
       補充：Jerry 一起，Chu 後製

    2. Natural-language fallback: use the first sentence as title and full text as brief.
    """

    FIELD_ALIASES = {
        "customer_name": ["客戶", "客戶名稱", "客戶歸屬"],
        "title": ["案名", "標題", "案件"],
        "job_type": ["類型", "案型"],
        "due_date": ["日期/交期", "日期", "交期", "檔期"],
        "brian_exec": ["Brian出工", "我有沒有要親自做", "Brian是否出工"],
        "notes": ["補充", "備註"],
    }

    def parse(self, message: str, *, source: str = "telegram") -> dict[str, Any]:
        text = message.strip()
        fields = self._parse_structured_lines(text)

        title = fields.get("title") or self._fallback_title(text)
        customer_name = fields.get("customer_name", "")
        raw_brief = self._build_brief(text, fields)

        result = {
            "title": title,
            "source": source,
            "customer_name": customer_name,
            "raw_brief": raw_brief,
            "metadata": {
                "job_type": fields.get("job_type"),
                "due_date": fields.get("due_date"),
                "brian_exec_hint": fields.get("brian_exec"),
                "notes": fields.get("notes"),
                "structured_fields": fields,
            },
        }
        return result

    def _parse_structured_lines(self, text: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for line in text.splitlines():
            if "：" not in line and ":" not in line:
                continue
            parts = re.split(r"[:：]", line, maxsplit=1)
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            if not key or not value:
                continue
            mapped = self._map_key(key)
            if mapped:
                parsed[mapped] = value
        return parsed

    def _map_key(self, key: str) -> str | None:
        for canonical, aliases in self.FIELD_ALIASES.items():
            if key == canonical or key in aliases:
                return canonical
        return None

    def _fallback_title(self, text: str) -> str:
        first_line = text.splitlines()[0].strip() if text.splitlines() else text
        if len(first_line) <= 80:
            return first_line or "未命名案件"
        return first_line[:80]

    def _build_brief(self, original_text: str, fields: dict[str, str]) -> str:
        lines = []
        if fields.get("job_type"):
            lines.append(f"類型：{fields['job_type']}")
        if fields.get("due_date"):
            lines.append(f"日期/交期：{fields['due_date']}")
        if fields.get("brian_exec"):
            lines.append(f"Brian出工：{fields['brian_exec']}")
        if fields.get("notes"):
            lines.append(f"補充：{fields['notes']}")
        lines.append(f"原始訊息：{original_text}")
        return "\n".join(lines)
