---
name: hermes-layered-memory-v2-phase-progression
description: Continue Hermes layered_memory V2 without losing the phase order or repeating already-landed bootstrap work.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, layered-memory, hermes-agent, sqlite, fts5, testing]
---

# Hermes Layered Memory V2 Phase Progression

## When to use
Use this when extending `plugins/memory/layered_memory/` in `hermes-agent`, especially after the initial bootstrap already exists and you need to keep pushing the next phase instead of redoing skeleton work.

## Current known landed baseline
Assume these are already present and should be extended, not reinvented:
- `LayeredMemoryStore` with SQLite + FTS5 storage
- scoped retrieval via `LayeredMemoryRetrieval`
- `sync_turn()` minimal working-memory capture
- `on_session_end()` archive summary write
- `on_pre_compress()` compact summary
- `allowed_layers` query filter
- query-time lifecycle updates for `access_count` and `last_accessed_at`
- conservative Layer 1 -> Layer 0 candidate annotation via `LayeredMemoryPromotion`
- archive fallback in `prefetch()` when working/durable results are empty
- `list_layer0_candidates()` for inspectable promotion candidates
- `system_prompt_block()` surfacing Layer 0 candidates for operator-visible prompt context
- conservative supersede handling for conflicting Layer 0 candidates to reduce split-brain truth
- stale-candidate demotion using lifecycle signals so old unaccessed candidates fall back to `state=stale`, `tier=working`
- provider maintenance runs before `system_prompt_block()` / `prefetch()` so stale candidates are demoted before surfacing or recall
- explicit operator tools:
  - `layered_memory_list_candidates`
  - `layered_memory_search`
  - `layered_memory_status`
- MemoryManager integration coverage proving layered-memory tools route through manager-level tool collection/dispatch, not only direct provider calls

## Files to inspect first
- `plugins/memory/layered_memory/provider.py`
- `plugins/memory/layered_memory/store.py`
- `plugins/memory/layered_memory/retrieval.py`
- `plugins/memory/layered_memory/extractor.py`
- `plugins/memory/layered_memory/promotion.py`
- `tests/plugins/memory/test_layered_memory_provider.py`
- `tests/agent/test_memory_provider.py`

## Proven implementation order
Do not jump straight to auto-promotion or vector retrieval.
Use this order:

1. Add/expand targeted tests first
2. Implement conservative behavior only
3. Verify targeted provider tests
4. Verify provider integration tests
5. Only then move to the next governance phase

## Proven test-first slices
### 1. Retrieval fallback slice
If continuity queries should remember prior sessions, add a failing test showing:
- working-layer search returns nothing
- archive row exists
- `prefetch()` still returns a context block

Then implement fallback in `provider.prefetch()` by retrying retrieval with `include_archive=True` only after the working/durable query is empty.

### 2. Lifecycle slice
If lifecycle fields exist but are not used, add a failing store test showing:
- first query returns row with initial lifecycle values
- second query increments `access_count`
- `last_accessed_at` becomes non-null

Implement lifecycle updates in the store, ideally through a helper such as `_apply_access_update()` so future decay/promotion logic can reuse the path.

### 3. Promotion candidate slice
If Layer 1 -> Layer 0 promotion is still placeholder-only:
- add a failing provider test using a durable user instruction (preferences/decisions work best)
- assert the saved row gets:
  - `metadata.layer0_candidate = true`
  - `promotion_stage = candidate`
  - upgraded `tier` such as `core_candidate`
  - raised `importance` / `confidence`

Implement this in a conservative annotator, not a writer to Layer 0. The safe step is candidate marking, not automatic canonical promotion.

### 4. Inspectable candidate surface
Do not leave candidates buried in metadata only.
Add a failing test for a store method such as `list_layer0_candidates()` and sort by:
- `importance`
- `confidence`
- `access_count`
- `updated_at`

This gives operators and later workflows a visible promotion queue.

### 5. Operator-visible promotion surfacing
After candidate listing exists, do not stop there.
Add a failing provider test showing `system_prompt_block()` includes:
- provider status/context
- active scope
- a short `Layer 0 候選` section
- the most important candidate abstracts

Implement this in `provider.system_prompt_block()` using `list_layer0_candidates()` with a small limit (for example 3). Keep this section informative, not noisy; do not duplicate full retrieved context here.

### 6. Contradiction / supersede slice
To prevent split-brain truth, add a failing provider/store test showing:
- an earlier durable candidate exists
- a new conflicting candidate in the same scope/category is written
- the older candidate becomes `superseded`
- `superseded_by_id` / `invalidated_at` are set
- candidate listings and normal queries exclude superseded rows

Implement this with a conservative store helper such as `supersede_conflicting_memories()` and call it only after a new row is written and confirmed as a Layer 0 candidate.

Keep promotion conservative. Good candidate signals:
- category in `preference`, `decision`, `project`, `identity`
- durable wording such as `記得`, `之後`, `未來`, `主路`, `fork`, `偏好`, `不要再`, `固定`, `一律`, or English equivalents like `remember`, `always`, `default`, `prefer`, `from now on`
- confidence >= 0.6 and importance >= 0.55 before upgrading to candidate

Avoid auto-promoting weak conversational noise.

### 7. Stale-candidate demotion slice
Once candidate surfacing and supersede logic exist, add a failing store/provider test showing:
- an old unaccessed candidate exists
- maintenance runs before prompt/retrieval surfacing
- the candidate is demoted to `state = stale`
- `tier` falls back to `working`
- `importance` decreases
- metadata records a demotion reason such as `demoted_stale_candidate`

Implement a conservative store helper such as `demote_stale_candidates()` keyed off lifecycle signals (`last_accessed_at`, `updated_at`, `access_count`).
Run this maintenance before `system_prompt_block()` and `prefetch()` so stale candidates disappear from operator-visible promotion surfaces automatically.

### 8. Operator inspection tool slice
Do not stop at prompt-only surfacing. Add failing tests for explicit provider tools:
- `layered_memory_list_candidates`
- `layered_memory_search`

Recommended behavior:
- both tools return JSON with `success`, active `scope`, and result rows
- `layered_memory_search` accepts `query`, `limit`, and `include_archive`
- candidate-list tool respects maintenance first, so stale candidates are demoted before listing

These tools create a reusable operator/control-plane surface instead of forcing every workflow to inspect raw SQLite rows.

### 9. Manager / operator integration slice
After provider-local tools work, add failing tests that prove the tools are reachable through `MemoryManager`, not just by calling the provider directly.

Minimum coverage:
- `MemoryManager.get_all_tool_schemas()` includes:
  - `layered_memory_list_candidates`
  - `layered_memory_search`
  - `layered_memory_status`
- `MemoryManager.handle_tool_call()` correctly routes layered-memory status/tool calls to the provider
- the routed status response includes:
  - active `scope`
  - counts for `confirmed`, `archive`, `working`, `stale`, `superseded`, `layer0_candidates`
  - `top_candidates`

Implement a provider helper such as `_build_status_payload()` and expose a `layered_memory_status` tool instead of forcing higher-level workflows to inspect raw rows or duplicate counting logic.

This is the first reusable integration point for future dashboard/operator surfaces.

## Verification commands
Always activate the venv first:
```bash
source venv/bin/activate
python -m pytest tests/plugins/memory/test_layered_memory_provider.py -q
python -m pytest tests/plugins/memory/test_layered_memory_provider.py tests/agent/test_memory_provider.py -q
python -m pytest tests/plugins/memory/ tests/agent/test_memory_provider.py tests/agent/test_memory_user_id.py -q
```

Known good checkpoints:
- `59 passed` across the two targeted test files after lifecycle + archive fallback + promotion candidate surfacing
- `61 passed` across the two targeted test files after system-prompt candidate surfacing + supersede governance
- `65 passed` across `tests/plugins/memory/test_layered_memory_provider.py tests/agent/test_memory_provider.py -q` after stale-candidate demotion + operator inspection tools
- `67 passed` across `tests/plugins/memory/test_layered_memory_provider.py tests/agent/test_memory_provider.py -q` after adding `layered_memory_status` and manager-level tool-routing coverage
- broader verification currently reaches `167 passed, 2 failed`, where the remaining failures are unrelated baseline issues in `tests/agent/test_memory_user_id.py`
- root cause of those two baseline failures:
  - `test_multiple_providers_all_receive_user_id` imports `agent.builtin_memory_provider.BuiltinMemoryProvider`, but that module/class no longer exists in the repo (stale test import / stale architecture reference)
  - `test_gateway_user_id_overrides_peer_name` expects Honcho to always override `peer_name` with `user_id`, but current Honcho policy only applies `user_id` when `cfg.peer_name` is empty; this is confirmed by `tests/honcho_plugin/test_session.py::TestToolsModeInitBehavior::{test_explicit_peer_name_not_overridden_by_user_id,test_user_id_used_when_no_peer_name}`

## Pitfalls learned
- Do not claim the next phase is done without actually running the tests.
- Do not stop at metadata-only promotion flags; add a readable candidate listing surface.
- Do not stop at store-only candidate listing; surface the most important candidates in `system_prompt_block()` so operators can see them immediately.
- Do not stop at prompt-only surfacing once operators need control; add explicit provider tools (`layered_memory_list_candidates`, `layered_memory_search`, `layered_memory_status`) for inspection and review flows.
- Once provider-local tools exist, verify they route through `MemoryManager`; otherwise the work is still stranded at provider scope and not yet reusable by higher-level operator surfaces.
- Do not let maintenance/state-count logic leak into future dashboards or managers; centralize it in a provider helper/status payload so higher layers can consume one stable JSON contract.
- Do not replace working-memory retrieval with archive retrieval; archive should be fallback-only.
- Do not auto-write into Layer 0 yet; candidate marking is the safe intermediate phase.
- When superseding conflicting durable candidates, make sure normal retrieval and candidate listing both exclude `superseded` rows, or split-brain truth will still leak into recall.
- Repo-wide unrelated failures may exist; keep verification scoped and explicitly distinguish baseline noise from the layered-memory changes.

## Recommended next phases after this baseline
1. Make promotion candidates visible in operator/retrieval flows, not just store APIs
2. Add contradiction/supersede handling to reduce split-brain truth
3. Add decay/staleness policy using lifecycle fields
4. Expand verification beyond targeted provider tests only after governance logic lands
