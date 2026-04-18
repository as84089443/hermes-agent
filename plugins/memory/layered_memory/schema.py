from __future__ import annotations

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS layered_memory_items (
    id TEXT PRIMARY KEY,
    scope_type TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    category TEXT NOT NULL,
    layer TEXT NOT NULL DEFAULT 'working',
    tier TEXT NOT NULL DEFAULT 'working',
    state TEXT NOT NULL DEFAULT 'confirmed',
    abstract TEXT NOT NULL,
    overview TEXT DEFAULT '',
    content TEXT DEFAULT '',
    source TEXT NOT NULL,
    source_session_id TEXT,
    source_message_id TEXT,
    confidence REAL NOT NULL DEFAULT 0.5,
    importance REAL NOT NULL DEFAULT 0.5,
    access_count INTEGER NOT NULL DEFAULT 0,
    injection_count INTEGER NOT NULL DEFAULT 0,
    suppressed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed_at TEXT,
    valid_from TEXT,
    valid_until TEXT,
    supersedes_id TEXT,
    superseded_by_id TEXT,
    invalidated_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_layered_memory_scope ON layered_memory_items(scope_type, scope_id);
CREATE INDEX IF NOT EXISTS idx_layered_memory_layer_tier ON layered_memory_items(layer, tier);
CREATE INDEX IF NOT EXISTS idx_layered_memory_category ON layered_memory_items(category);
CREATE INDEX IF NOT EXISTS idx_layered_memory_state ON layered_memory_items(state);
CREATE INDEX IF NOT EXISTS idx_layered_memory_last_accessed ON layered_memory_items(last_accessed_at);

CREATE VIRTUAL TABLE IF NOT EXISTS layered_memory_items_fts USING fts5(
    abstract,
    overview,
    content,
    content='layered_memory_items',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS layered_memory_items_ai AFTER INSERT ON layered_memory_items BEGIN
    INSERT INTO layered_memory_items_fts(rowid, abstract, overview, content)
    VALUES (new.rowid, new.abstract, new.overview, new.content);
END;

CREATE TRIGGER IF NOT EXISTS layered_memory_items_ad AFTER DELETE ON layered_memory_items BEGIN
    INSERT INTO layered_memory_items_fts(layered_memory_items_fts, rowid, abstract, overview, content)
    VALUES ('delete', old.rowid, old.abstract, old.overview, old.content);
END;

CREATE TRIGGER IF NOT EXISTS layered_memory_items_au AFTER UPDATE ON layered_memory_items BEGIN
    INSERT INTO layered_memory_items_fts(layered_memory_items_fts, rowid, abstract, overview, content)
    VALUES ('delete', old.rowid, old.abstract, old.overview, old.content);
    INSERT INTO layered_memory_items_fts(rowid, abstract, overview, content)
    VALUES (new.rowid, new.abstract, new.overview, new.content);
END;
"""
