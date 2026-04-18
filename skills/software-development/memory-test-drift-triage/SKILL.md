---
name: memory-test-drift-triage
description: Triage failing Hermes memory/provider tests to separate real regressions from stale test drift, policy mismatch, and removed-architecture references.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [testing, debugging, hermes, memory, honcho, stale-tests]
---

# Memory Test Drift Triage

Use when Hermes memory-related tests fail and it is unclear whether the failure is a real regression or stale test/docs drift.

## When this skill applies
- `tests/agent/test_memory_user_id.py` or other memory/provider tests fail
- the failure mentions missing classes/modules that no longer exist
- a provider test expectation conflicts with another passing test suite
- Honcho/Mem0/memory-provider behavior looks inconsistent across test files

## Core method
Do not patch the failing test immediately. First prove whether the test is stale, the code is wrong, or the docs/comments drifted.

## Procedure
1. Reproduce the exact failing tests.
   - Example:
     - `source venv/bin/activate && python -m pytest tests/agent/test_memory_user_id.py -q`

2. Read the failing test file fully.
   - Look for imports of classes/modules that may have been removed.
   - Look for assertions that encode behavior policy.

3. Search the repo for the referenced symbol and policy.
   - Use `search_files` for:
     - missing class/module names (e.g. `BuiltinMemoryProvider`, `builtin_memory_provider`)
     - policy conditions (e.g. `if _gw_user_id and not cfg.peer_name`)
   - If the symbol does not exist anywhere, treat it as stale test drift unless proven otherwise.

4. Cross-check with the provider's authoritative tests.
   - For Honcho user/peer-name behavior, compare against `tests/honcho_plugin/test_session.py`.
   - If the provider-specific tests pass and the higher-level test disagrees, the higher-level test is likely stale.

5. Inspect docs/comments for architecture drift.
   - Search `agent/memory_provider.py`, `agent/memory_manager.py`, and related comments for old class names or outdated assumptions.
   - Fix these alongside the test to avoid future confusion.

## Findings this skill encodes
### A. Removed built-in provider class references
If a test imports `agent.builtin_memory_provider.BuiltinMemoryProvider` but no such module/class exists in the repo:
- do not recreate the old class just to satisfy the test
- replace the test with a provider double that uses `name == "builtin"` if the behavior under test is `MemoryManager`'s builtin/external routing contract

### B. Honcho peer_name policy
Current Honcho policy is:
- if gateway `user_id` exists and `cfg.peer_name` is empty, use `user_id` as fallback peer identity
- if `cfg.peer_name` is explicitly set, do NOT override it with `user_id`

So tests should cover:
- missing peer_name -> user_id used
- explicit peer_name -> preserved
- no user_id -> existing peer_name preserved

### C. Mock quality for Honcho config tests
When testing Honcho initialization with mocked config, set enough fields to avoid irrelevant validation noise:
- `enabled = True`
- `api_key` or `base_url`
- `peer_name` as needed
- `recall_mode = "tools"`
- `init_on_session_start = False`
- `raw = {}`

This keeps the test focused on peer-name/user-id behavior instead of unrelated config validation.

## Verification
After fixes:
1. Run the directly affected tests:
   - `python -m pytest tests/agent/test_memory_user_id.py tests/agent/test_memory_provider.py tests/plugins/memory/test_layered_memory_provider.py -q`
2. Run the broader memory suite:
   - `python -m pytest tests/plugins/memory/ tests/agent/test_memory_provider.py tests/agent/test_memory_user_id.py -q`

## Success criteria
- failing memory tests pass
- provider-specific policy tests still pass
- stale architecture references are removed from tests and comments
- no fix was made by reintroducing dead architecture purely for compatibility
