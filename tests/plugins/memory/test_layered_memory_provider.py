import json
from pathlib import Path

from plugins.memory import discover_memory_providers, load_memory_provider
from plugins.memory.layered_memory import LayeredMemoryProvider
from plugins.memory.layered_memory.store import LayeredMemoryStore


def test_layered_memory_provider_discovery_and_load():
    providers = {name: (desc, available) for name, desc, available in discover_memory_providers()}

    assert "layered_memory" in providers
    desc, available = providers["layered_memory"]
    assert "Layer 1" in desc
    assert available is True

    provider = load_memory_provider("layered_memory")
    assert isinstance(provider, LayeredMemoryProvider)


def test_layered_memory_provider_initializes_profile_scoped_store(tmp_path):
    provider = LayeredMemoryProvider()

    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    assert provider._store is not None
    assert provider._store.db_path == tmp_path / "layered_memory.db"
    assert provider._active_scope == ("profile", "coder")


def test_layered_memory_provider_system_prompt_surfaces_layer0_candidates(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.sync_turn(
        "之後都走 as84089443 fork 主路，不要再回報舊 upstream PR",
        "收到，我之後會只沿著 fork 主路推進",
        session_id="session-1",
    )

    block = provider.system_prompt_block()

    assert "Layered Memory" in block
    assert "Layer 0 候選" in block
    assert "as84089443 fork 主路" in block


def test_layered_memory_provider_system_prompt_runs_stale_candidate_maintenance(tmp_path):
    provider = LayeredMemoryProvider(config={"stale_candidate_days": 30})
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    stale_id = provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="decision",
        abstract="Use old upstream lane",
        overview="Outdated lane decision",
        content="Use the old upstream lane.",
        source="sync_turn",
        tier="core_candidate",
        importance=0.8,
        confidence=0.8,
        metadata={"layer0_candidate": True, "promotion_stage": "candidate"},
    )
    provider._store._conn.execute(
        "UPDATE layered_memory_items SET updated_at = ?, last_accessed_at = ?, access_count = 0 WHERE id = ?",
        ("2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00", stale_id),
    )
    provider._store._conn.commit()

    block = provider.system_prompt_block()

    assert "Use old upstream lane" not in block
    row = provider._store._conn.execute(
        "SELECT state, metadata_json FROM layered_memory_items WHERE id = ?",
        (stale_id,),
    ).fetchone()
    assert row["state"] == "stale"
    assert 'demoted_stale_candidate' in row["metadata_json"]


def test_layered_memory_provider_exposes_candidate_inspection_tool(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    provider.sync_turn(
        "之後都走 as84089443 fork 主路，不要再回報舊 upstream PR",
        "收到，我之後會只沿著 fork 主路推進",
        session_id="session-1",
    )

    schemas = provider.get_tool_schemas()
    assert any(schema["name"] == "layered_memory_list_candidates" for schema in schemas)

    result = json.loads(provider.handle_tool_call("layered_memory_list_candidates", {"limit": 5}))
    assert result["success"] is True
    assert result["scope"] == {"type": "profile", "id": "coder"}
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["metadata"]["promotion_stage"] == "candidate"


def test_layered_memory_provider_exposes_search_tool(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="decision",
        abstract="Current fork is as84089443/hermes-agent",
        overview="Main operating lane is the user's fork.",
        content="Use the user's fork as the primary operating lane instead of the old upstream PR path.",
        source="manual",
    )
    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="session-summary",
        abstract="Archive summary retained old lane discussion",
        overview="Session archive recorded the lane handoff.",
        content="Earlier session archive says the fork lane replaced the old upstream lane.",
        source="session_end",
        layer="archive",
        tier="peripheral",
        metadata={"summary_kind": "session_end"},
    )

    schemas = provider.get_tool_schemas()
    assert any(schema["name"] == "layered_memory_search" for schema in schemas)

    result = json.loads(
        provider.handle_tool_call(
            "layered_memory_search",
            {"query": "fork lane", "limit": 5, "include_archive": True},
        )
    )
    assert result["success"] is True
    assert result["scope"] == {"type": "profile", "id": "coder"}
    assert len(result["results"]) >= 2
    assert any(row["layer"] == "archive" for row in result["results"])


def test_layered_memory_provider_exposes_status_tool(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    provider.sync_turn(
        "之後都走 as84089443 fork 主路，不要再回報舊 upstream PR",
        "收到，我之後會只沿著 fork 主路推進",
        session_id="session-1",
    )
    provider.on_session_end([
        {"role": "user", "content": "請沿著 as84089443 這條路繼續"},
        {"role": "assistant", "content": "我會以 fork 作為主路繼續推進"},
    ])

    schemas = provider.get_tool_schemas()
    assert any(schema["name"] == "layered_memory_status" for schema in schemas)

    result = json.loads(provider.handle_tool_call("layered_memory_status", {}))
    assert result["success"] is True
    assert result["scope"] == {"type": "profile", "id": "coder"}
    assert result["counts"]["confirmed"] >= 1
    assert result["counts"]["archive"] >= 1
    assert result["counts"]["layer0_candidates"] >= 1
    assert result["top_candidates"][0]["metadata"]["promotion_stage"] == "candidate"


def test_layered_memory_provider_prefetch_returns_scoped_memory_context(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="project",
        abstract="Current fork is as84089443/hermes-agent",
        overview="Main operating lane is the user's fork.",
        content="Use the user's fork as the primary operating lane instead of the old upstream PR path.",
        source="manual",
        metadata={"layer0_candidate": False},
    )
    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="other-profile",
        category="project",
        abstract="This should not leak",
        overview="wrong scope",
        content="wrong scope",
        source="manual",
        metadata={"layer0_candidate": False},
    )

    result = provider.prefetch("which fork should I use?")

    assert "Layered Working Memory" in result
    assert "Current fork is as84089443/hermes-agent" in result
    assert "Layer 0 候選" not in result
    assert "This should not leak" not in result


def test_layered_memory_provider_prefetch_skips_low_signal_queries(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="project",
        abstract="Current fork is as84089443/hermes-agent",
        overview="Main operating lane is the user's fork.",
        content="Use the user's fork as the primary operating lane instead of the old upstream PR path.",
        source="manual",
    )

    assert provider.prefetch("ok") == ""


def test_layered_memory_provider_prefetch_falls_back_to_archive_when_working_empty(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )
    provider._store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="session-summary",
        abstract="Earlier session used fork-first operating lane",
        overview="Archive summary says the fork is the primary lane.",
        content="The last completed session established that the as84089443 fork is the main lane.",
        source="session_end",
        layer="archive",
        tier="peripheral",
        metadata={"summary_kind": "session_end"},
    )

    result = provider.prefetch("what lane did we agree to use last time?")

    assert "Layered Working Memory" in result
    assert "Earlier session used fork-first operating lane" in result


def test_layered_memory_provider_mirrors_builtin_memory_writes_as_layer0_candidates(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.on_memory_write(
        "add",
        "user",
        "When work is moved to as84089443 fork, do not keep reporting old upstream PR state.",
    )

    rows = provider._store.query_memories(
        query="upstream PR",
        scope_type="profile",
        scope_id="coder",
        limit=5,
    )

    assert len(rows) == 1
    assert rows[0]["category"] == "preference"
    assert rows[0]["metadata"]["layer0_candidate"] is True
    assert rows[0]["source"] == "builtin_memory:user:add"


def test_layered_memory_store_creates_schema_and_filters_suppressed_rows(tmp_path):
    store = LayeredMemoryStore(tmp_path / "layered_memory.db")

    store.upsert_memory(
        scope_type="project",
        scope_id="repo-a",
        category="decision",
        abstract="Use pnpm",
        overview="repo-a uses pnpm",
        content="repo-a package manager is pnpm",
        source="manual",
        suppressed=1,
    )
    store.upsert_memory(
        scope_type="project",
        scope_id="repo-a",
        category="decision",
        abstract="Use uv",
        overview="repo-a uses uv for Python deps",
        content="repo-a uses uv for Python dependencies",
        source="manual",
    )

    rows = store.query_memories(
        query="uses",
        scope_type="project",
        scope_id="repo-a",
        limit=10,
    )

    assert [row["abstract"] for row in rows] == ["Use uv"]

    table_names = {
        row[0]
        for row in store._conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        ).fetchall()
    }
    assert "layered_memory_items" in table_names
    assert "layered_memory_items_fts" in table_names


def test_layered_memory_store_upsert_updates_existing_memory(tmp_path):
    store = LayeredMemoryStore(tmp_path / "layered_memory.db")

    memory_id = store.upsert_memory(
        scope_type="project",
        scope_id="repo-a",
        category="decision",
        abstract="Use pnpm",
        overview="repo-a uses pnpm",
        content="repo-a package manager is pnpm",
        source="manual",
        metadata={"version": 1},
    )
    memory_id_2 = store.upsert_memory(
        scope_type="project",
        scope_id="repo-a",
        category="decision",
        abstract="Use pnpm",
        overview="repo-a uses pnpm workspace commands",
        content="repo-a package manager is pnpm and workspace commands should use pnpm -w",
        source="manual",
        metadata={"version": 2},
    )

    assert memory_id_2 == memory_id
    rows = store.query_memories(
        query="workspace commands",
        scope_type="project",
        scope_id="repo-a",
        limit=5,
    )
    assert len(rows) == 1
    assert rows[0]["overview"] == "repo-a uses pnpm workspace commands"
    assert rows[0]["metadata"]["version"] == 2


def test_layered_memory_store_query_updates_access_lifecycle_fields(tmp_path):
    store = LayeredMemoryStore(tmp_path / "layered_memory.db")

    store.upsert_memory(
        scope_type="project",
        scope_id="repo-a",
        category="decision",
        abstract="Use uv",
        overview="repo-a uses uv",
        content="repo-a uses uv for Python dependencies",
        source="manual",
    )

    before = store.query_memories(
        query="uv",
        scope_type="project",
        scope_id="repo-a",
        limit=5,
    )
    assert before[0]["access_count"] == 0
    assert before[0]["last_accessed_at"] is None

    after = store.query_memories(
        query="uv",
        scope_type="project",
        scope_id="repo-a",
        limit=5,
    )
    assert after[0]["access_count"] == 1
    assert after[0]["last_accessed_at"] is not None


def test_layered_memory_provider_on_session_end_writes_archive_summary(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.on_session_end([
        {"role": "system", "content": "ignore"},
        {"role": "user", "content": "請沿著 as84089443 這條路繼續"},
        {"role": "assistant", "content": "我會以 fork 作為主路繼續推進"},
    ])

    rows = provider._store.query_memories(
        query="as84089443",
        scope_type="profile",
        scope_id="coder",
        limit=5,
        allowed_layers=["archive"],
    )
    assert len(rows) == 1
    assert rows[0]["category"] == "session-summary"
    assert rows[0]["layer"] == "archive"
    assert rows[0]["metadata"]["summary_kind"] == "session_end"
    assert rows[0]["metadata"]["session_id"] == "session-1"


def test_layered_memory_provider_sync_turn_writes_working_memory(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.sync_turn(
        "之後都走 as84089443 fork 主路，不要再回報舊 upstream PR",
        "收到，我之後會只沿著 fork 主路推進",
        session_id="session-1",
    )

    rows = provider._store.query_memories(
        query="upstream PR",
        scope_type="profile",
        scope_id="coder",
        limit=5,
        allowed_layers=["working"],
    )
    assert len(rows) == 1
    assert rows[0]["layer"] == "working"
    assert rows[0]["category"] == "decision"
    assert rows[0]["source"] == "sync_turn"
    assert rows[0]["metadata"]["summary_kind"] == "sync_turn"
    assert rows[0]["metadata"]["session_id"] == "session-1"
    assert rows[0]["metadata"]["layer0_candidate"] is True
    assert rows[0]["tier"] == "core_candidate"
    assert rows[0]["importance"] >= 0.75
    assert rows[0]["confidence"] >= 0.75

    candidates = provider._store.list_layer0_candidates(
        scope_type="profile",
        scope_id="coder",
        limit=5,
    )
    assert len(candidates) == 1
    assert candidates[0]["abstract"] == rows[0]["abstract"]
    assert candidates[0]["metadata"]["promotion_stage"] == "candidate"


def test_layered_memory_provider_sync_turn_skips_low_signal_messages(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.sync_turn("ok", "好", session_id="session-1")

    rows = provider._store.query_memories(
        query="ok",
        scope_type="profile",
        scope_id="coder",
        limit=5,
        allowed_layers=["working"],
    )
    assert rows == []


def test_layered_memory_provider_sync_turn_supersedes_conflicting_candidate(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    provider.sync_turn(
        "之後都走 as84089443 fork 主路，不要再回報舊 upstream PR",
        "收到，我會沿著 fork 主路推進",
        session_id="session-1",
    )
    provider.sync_turn(
        "更新一下，之後改成回 upstream main，不要再走 fork 主路",
        "收到，我之後改回 upstream main",
        session_id="session-2",
    )

    active_rows = provider._store.query_memories(
        query="upstream main",
        scope_type="profile",
        scope_id="coder",
        limit=5,
        allowed_layers=["working"],
    )
    assert len(active_rows) == 1
    assert "upstream main" in active_rows[0]["abstract"]
    assert active_rows[0]["state"] == "confirmed"

    candidates = provider._store.list_layer0_candidates(
        scope_type="profile",
        scope_id="coder",
        limit=10,
    )
    assert len(candidates) == 1
    assert "upstream main" in candidates[0]["abstract"]

    raw_rows = provider._store._conn.execute(
        "SELECT abstract, state, superseded_by_id FROM layered_memory_items ORDER BY created_at ASC"
    ).fetchall()
    assert raw_rows[0]["state"] == "superseded"
    assert raw_rows[0]["superseded_by_id"] is not None
    assert raw_rows[1]["state"] == "confirmed"


def test_layered_memory_store_demotes_stale_candidates(tmp_path):
    store = LayeredMemoryStore(tmp_path / "layered_memory.db")

    fresh_id = store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="decision",
        abstract="Keep using fork lane",
        overview="Current durable lane remains fork-first",
        content="Use the fork lane by default.",
        source="sync_turn",
        tier="core_candidate",
        importance=0.8,
        confidence=0.8,
        metadata={"layer0_candidate": True, "promotion_stage": "candidate"},
    )
    stale_id = store.upsert_memory(
        scope_type="profile",
        scope_id="coder",
        category="decision",
        abstract="Use old upstream lane",
        overview="Outdated lane decision",
        content="Use the old upstream lane.",
        source="sync_turn",
        tier="core_candidate",
        importance=0.8,
        confidence=0.8,
        metadata={"layer0_candidate": True, "promotion_stage": "candidate"},
    )
    store._conn.execute(
        "UPDATE layered_memory_items SET updated_at = ?, last_accessed_at = ?, access_count = 0 WHERE id = ?",
        ("2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00", stale_id),
    )
    store._conn.commit()

    changed = store.demote_stale_candidates(
        scope_type="profile",
        scope_id="coder",
        stale_before="2025-01-01T00:00:00+00:00",
    )

    assert changed == 1
    candidates = store.list_layer0_candidates(scope_type="profile", scope_id="coder", limit=10)
    assert len(candidates) == 1
    assert candidates[0]["id"] == fresh_id

    stale_row = store._conn.execute(
        "SELECT state, tier, importance, metadata_json FROM layered_memory_items WHERE id = ?",
        (stale_id,),
    ).fetchone()
    assert stale_row["state"] == "stale"
    assert stale_row["tier"] == "working"
    assert stale_row["importance"] < 0.8
    assert 'demoted_stale_candidate' in stale_row["metadata_json"]


def test_layered_memory_provider_on_pre_compress_returns_compact_summary(tmp_path):
    provider = LayeredMemoryProvider()
    provider.initialize(
        "session-1",
        hermes_home=str(tmp_path),
        platform="cli",
        agent_identity="coder",
    )

    result = provider.on_pre_compress([
        {"role": "user", "content": "幫我記得未來都走 fork 主路"},
        {"role": "assistant", "content": "我會把 fork 作為主路"},
    ])

    assert "Layered memory pre-compress summary" in result
    assert "fork" in result
