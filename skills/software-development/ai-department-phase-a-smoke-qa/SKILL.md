---
name: ai-department-phase-a-smoke-qa
description: Run the reusable Phase A smoke QA suite for Hermes dashboard + AI Department OS, generate report artifacts, and validate the first regression-grade operating loop.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qa, smoke-test, hermes-dashboard, ai-department-os, regression, project-specific]
---

# AI Department Phase A Smoke QA

Use when working on `/Users/brian/dev/ai-department-os` and the goal is to verify the first regression-grade smoke loop across Hermes dashboard and AI Department OS.

## What this validates

Five flows:
1. Hermes dashboard home
2. Sessions
3. Config / Env
4. AI Department OS projects
5. approvals decision flow

This is the bridge from:
- "I opened the page once"
into
- repeatable
- verifiable
- regression-friendly QA

## Canonical artifacts

Primary files:
- `scripts/qa/run_phase_a_smoke.py`
- `scripts/qa/run-phase-a-smoke.sh`
- `docs/qa/phase-a-smoke-checklist.md`
- `docs/plans/2026-04-13-phase-a-smoke-qa-artifact.md`

Report output:
- `qa-output/phase-a-smoke/<timestamp>/report.md`
- `qa-output/phase-a-smoke/<timestamp>/report.json`
- `qa-output/phase-a-smoke/<timestamp>/logs/`

## How to run

From `/Users/brian/dev/ai-department-os`:

```bash
./scripts/qa/run-phase-a-smoke.sh
```

Useful variants:

```bash
# Reuse already-running services only
./scripts/qa/run-phase-a-smoke.sh --skip-start-services

# Remove the smoke-created project after the run
./scripts/qa/run-phase-a-smoke.sh --cleanup-created-project
```

## Service behavior

### Hermes dashboard
- prefers `http://127.0.0.1:9119`
- reuses an existing dashboard if `/api/status` is already healthy
- otherwise starts:

```bash
source venv/bin/activate && python -m hermes_cli.main dashboard --no-open --host 127.0.0.1 --port 9119
```

### AI Department OS
- prefers `http://127.0.0.1:3010`
- if an existing dev server is already reachable at `http://127.0.0.1:3000`, the smoke suite reuses it automatically
- otherwise starts:

```bash
npm run dev -- --hostname 127.0.0.1 --port 3010
```

## What the script actually asserts

### Flow 1 — Hermes dashboard home
- `GET /` returns 200
- HTML contains `Hermes Agent`
- `GET /api/status` returns required fields:
  - `version`
  - `hermes_home`
  - `config_path`
  - `env_path`
  - `active_sessions`
  - `gateway_running`

### Flow 2 — Sessions
- `GET /api/sessions` returns an array
- if at least one session exists, `GET /api/sessions/{id}/messages` returns a messages array
- empty session state is acceptable

### Flow 3 — Config / Env
- `GET /api/config/schema` is readable
- schema contains `model`
- category order contains `general`
- `GET /api/env` returns a non-empty object
- a sample env entry contains `is_set` and `tools`

### Flow 4 — AI Department OS projects
- creates a smoke project via `POST /api/intake`
- verifies it appears in `GET /api/projects`
- verifies workspace via `GET /api/projects/{id}`
- confirms project state becomes `approval_pending`
- confirms `/projects` and `/projects/{id}` render the expected decision-oriented content

### Flow 5 — approvals decision flow
- fetches project approvals via `GET /api/projects/{id}/approvals`
- sends `changes_requested` through `POST /api/approvals/{approvalId}/decision`
- verifies:
  - project state becomes `revise`
  - events contain `approval_decided`
  - `approval-prep` task becomes `needs_revision`
  - `/approvals` still renders the decision form language

## Why the default decision path is `changes_requested`

Use `changes_requested` as the default smoke path because it is the most stable and least disruptive regression path:
- lower side effects than pushing a project fully forward
- easy to assert (`revise`, `approval_decided`, `needs_revision`)
- keeps the suite closer to a safe QA loop

## Important pitfalls

1. Hermes dashboard is an SPA shell
- do not assume there are standalone page URLs like `/sessions` or `/config`
- use API checks for stability, not route-path assumptions

2. AI Department OS may already have a dev lock
- if `.next/dev/lock` blocks a second `next dev`, reuse the existing `http://127.0.0.1:3000` server instead
- the smoke script already does this fallback automatically

3. `POST /api/intake` response is not the final canonical state
- always verify canonical persisted state with `GET /api/projects/{id}`
- the project may be updated after creation into `approval_pending`

4. `GET /api/approval-queue` is not the best per-project assertion source
- for deterministic smoke tests, prefer `GET /api/projects/{id}/approvals`

5. Hermes Config / Env checks should stay read-only in smoke mode
- do not add PUT/DELETE env/config writes to the default suite

6. The smoke runner may be executed by macOS system `python3` (3.9)
- keep the script compatible with Python 3.9+
- if modern `X | None` type annotations are used, add `from __future__ import annotations`
- do not assume the launcher runs inside a Python 3.11 virtualenv

7. UI assertions must follow the current boss-mode wording, not stale labels
- `/projects` should assert stable decision-oriented sections like `Phase 表` and `先看這些待拍板案子`
- `/projects/[id]` should assert the summary cards `目前方向` / `目前階段` / `目前卡點`
- `/approvals` currently uses `送出決定`, not `送出決策`

## Verification standard

A good run should end with:
- exit code 0
- markdown + json report written under `qa-output/phase-a-smoke/...`
- all five flows passing
- optional cleanup deleting only the newly created smoke project folders

## When extending this skill

Natural next upgrades:
- add browser-based DOM assertions for dashboard SPA nav switching
- add optional matrix for `approved` and `rejected`
- wire this suite into tmux `smoke-qa` lane or cron/pre-demo workflow
