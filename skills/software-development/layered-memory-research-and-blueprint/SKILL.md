---
name: layered-memory-research-and-blueprint
description: Deep-study a candidate memory system and turn it into a Hermes-native layered-memory blueprint with anti-hype correction, current-state comparison, and phased migration.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, architecture, research, blueprint, distillation]
    related_skills: [deep-repo-distillation-blueprint, parallel-architecture-review, thinking-hound-mode]
---

# Layered Memory Research and Blueprint

Use when:
- the user wants to solve agent memory limits structurally, not by just raising caps
- a repo claims "three-layer memory" / long-term memory / hybrid recall and needs source-grounded evaluation
- you need to compare an external memory system against Hermes's current memory stack
- the deliverable should be a canonical architecture page or implementation blueprint

## Core rule
Do not trust the README's memory vocabulary.
Many memory repos blur together:
- content layers
- lifecycle tiers
- governance/storage layers

Always separate those axes before drawing conclusions.

## Research workflow

### Round 1 — map the candidate repo's claimed memory model
Read:
- README
- architecture docs
- metadata/schema files
- write path
- retrieval path
- decay/promotion/tiering files

Capture hypotheses only:
- what are the named layers?
- what are the named tiers?
- what is actually stored per item?
- what is injected vs merely retrievable?

### Round 2 — verify the actual implementation
Inspect source files for:
- write/create path
- merge/supersede path
- retrieval/ranking path
- invalidation/expiry path
- prompt injection path

Look for these exact questions:
- are the "layers" really separate stores, or just fields on one row?
- does promotion/demotion really run in the main path, or only in maintenance code?
- does the system truly retrieve different granularities, or mostly store them without using them?
- does the repo have dual sources of truth?

### Round 3 — inspect Hermes current memory model
Inspect Hermes for all current memory planes, not just the memory tool.
Minimum targets:
- built-in USER.md / MEMORY.md prompt injection
- memory tool limits and write rules
- memory manager / external provider contract
- session_search storage and recall path
- skills as procedural memory

Important questions:
- which parts are always-on prompt memory?
- which parts are retrieval-based?
- what refreshes mid-session vs only next session?
- what hard caps exist?
- what already acts like Layer 2 archive recall?

### Round 4 — anti-hype correction
Write explicitly:
- what the candidate repo genuinely solves
- what it overstates
- what should be copied directly
- what should be adapted carefully
- what should not be copied

This step is mandatory.

## Synthesis pattern for Hermes

When converting research into a Hermes-native design, prefer this structure:

### Layer 0 — Core Canonical Memory
Purpose:
- tiny, stable, always-injected facts
Examples:
- user preferences
- identity facts
- stable environment conventions

Implementation default:
- continue using USER.md / MEMORY.md
- keep frozen-at-session-start semantics for prompt-cache stability

### Layer 1 — Durable Working Memory
Purpose:
- important cross-session recall that should NOT live in the always-on prompt
Examples:
- active project context
- durable but revisable facts
- recurring repo/workspace conventions

Implementation default:
- retrieval-based external provider
- local SQLite canonical table first
- FTS5 first, vector later
- inject ephemerally per turn, not permanently in the system prompt

### Layer 2 — Archive / Session Evidence
Purpose:
- long-tail historical recall
Examples:
- past sessions
- transcript evidence
- archived summaries

Implementation default:
- reuse session DB / session_search as the archive backend
- summarize on demand
- avoid auto-injecting raw transcript

### Separate procedural plane
Keep skills separate from factual memory.
Do not collapse workflows and facts into one store.

## Design heuristics

1. The smallest and most expensive memory tier must stay tiny.
2. Most memory should be retrieval-based, not always-on.
3. Promotion into Layer 0 must be conservative.
4. Scope filters are mandatory:
- profile
- user
- project
- agent
5. Avoid dual-source ambiguity between markdown memory and provider memory.
6. Prefer append-only evidence + invalidation links over destructive overwrite.

## Recommended Hermes migration order

### Phase 1 — policy first
Define and lock in a dedicated Phase-1 policy package before writing the provider:
- what belongs in Layer 0 / 1 / 2
- what belongs in skills instead
- source-of-truth ownership per layer
- category taxonomy
- promotion / demotion rules
- retrieval trigger matrix
- scope rules and cross-scope prohibitions
- red-team guardrails against split-brain truth, scope leakage, prompt bloat, and skills/facts contamination

Good deliverable shape for this phase:
- one canonical blueprint page
- one implementation-plan page
- one Phase-1 policy package page that becomes the lock artifact before code work

Do not start storage work until these are explicit. This prevents rebuilding the memory problem with better storage but worse governance.

### Phase 2 — Layer 1 MVP
Build a single new provider behind Hermes's existing memory-provider interface.
Recommended file split:
- `provider.py`
- `store.py`
- `retrieval.py`
- `extractor.py`
- `promotion.py`
- `schema.py`
- `scopes.py`
- `migrations.py`
- `plugin.yaml`
- `__init__.py`

Start with:
- SQLite
- FTS5 + triggers
- no vector dependency required
- scoped prefetch/query path
- `on_memory_write()` mirror for Layer-0 candidates
- conservative `on_session_end()` archive/session-summary writes
- compact `on_pre_compress()` summary output
- a minimal `sync_turn()` path that captures only high-signal durable cues into Layer 1 working memory

Practical MVP heuristic learned in use:
- `sync_turn()` should start very conservatively
- only capture one working-memory row per turn at most
- look for explicit durable/continuity cues first (e.g. “remember”, “from now on”, “prefer”, “fork”, “main path”, “不要再”, “一律”)
- avoid broad freeform extraction until the store and retrieval behavior are stable

Delay aggressive working-memory auto-extraction until after the skeleton is stable.

### Phase 2 testing discipline
Before expanding behavior, get the skeleton green with focused tests around:
- plugin discovery / load
- provider initialize path
- scoped prefetch
- low-signal query skip
- builtin-memory mirroring into Layer-0 candidates
- session-end archive summary writes
- pre-compress compact summary output
- minimal sync-turn working-memory capture
- SQLite upsert/query semantics and layer filtering

When validating, prefer targeted provider + memory-manager tests first. Do not claim the whole repo memory/test surface is fixed if unrelated pre-existing failures remain elsewhere in the suite.

### Phase 3 — archive unification
Reframe session_search as Layer 2 archive recall under one policy umbrella.

### Phase 4 — lifecycle scoring
Add:
- recency
- access_count
- confidence
- importance
- stale decay
- supersession / invalidation

### Phase 5 — hybrid retrieval
Only after lexical retrieval works well:
- add vector backend
- add fusion/rerank if needed
- preserve fallback to lexical-only mode

## Deliverable format
Always produce:

1. Current-state diagnosis
- exact Hermes layers today
- exact caps/constraints
- exact injection behavior

2. Candidate-repo truth table
- real strengths
- hype / ambiguity
- source-level evidence

3. Hermes-native target architecture
- layer definitions
- scope model
- retrieval policy
- promotion/demotion rules

4. Migration sequence
- phased rollout
- risks
- verification matrix

## Good verification checks
- stable preferences persist without bloating the prompt
- project/user scope isolation prevents leakage
- temporary session facts do not get promoted into Layer 0
- archive recall works when Layer 1 misses
- prompt-cache behavior does not materially regress

## Pitfalls
- treating all memory as one blob
- copying another repo's terminology without separating its actual axes
- adding a retrieval store without a source-of-truth policy
- moving too much into always-on prompt memory
- mixing procedural memory with factual memory
