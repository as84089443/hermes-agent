---
name: ai-department-os-gsd-phase-ab-team-launch
description: Launch and verify a tmux-based multi-agent team for ai-department-os Phase A+B work, with fixed lane roles for smoke QA and phase-contract discipline.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-department-os, tmux, multi-agent, qa, phases, project-specific]
---

# AI Department OS GSD Phase A+B Team Launch

Use when:
- working in `/Users/brian/dev/ai-department-os`
- the user wants to run multiple Hermes agents like an AI team
- the current focus is Phase A + Phase B
  - Phase A: smoke QA becomes repeatable / verifiable / regression-friendly
  - Phase B: phase-based execution gets standardized into explicit gates and lanes

## What this setup creates

A tmux session with 5 windows:
- `commander` — overall phase controller
- `smoke-qa` — defines the 5 smoke flows and regression shape
- `app-surface` — maps real pages/routes/data prerequisites
- `process-guard` — formalizes spec/plan/execute/review/verify contract
- `verify` — final convergence and operability check

Each window launches `hermes -w` so parallel code work is less likely to conflict.

## Canonical files

Plan document:
- `docs/plans/2026-04-13-gsd-phase-a-b-team-operating-plan.md`

Prompt files:
- `docs/prompts/gsd-phase-ab/commander.md`
- `docs/prompts/gsd-phase-ab/smoke-qa.md`
- `docs/prompts/gsd-phase-ab/app-surface.md`
- `docs/prompts/gsd-phase-ab/process-guard.md`
- `docs/prompts/gsd-phase-ab/verifier.md`

Launcher:
- `scripts/launch-gsd-phase-ab-team.sh`

## Launch command

```bash
cd /Users/brian/dev/ai-department-os
./scripts/launch-gsd-phase-ab-team.sh
```

Optional:

```bash
# create session but do not attach
./scripts/launch-gsd-phase-ab-team.sh --no-attach

# custom session name
./scripts/launch-gsd-phase-ab-team.sh my-session
./scripts/launch-gsd-phase-ab-team.sh my-session --no-attach
```

## Verification workflow

For non-interactive verification, use `--no-attach`.
This is the safest way to test the launcher without taking over the current terminal.

Recommended checks:

```bash
bash -n scripts/launch-gsd-phase-ab-team.sh
./scripts/launch-gsd-phase-ab-team.sh gsd-phase-ab-verify --no-attach
tmux list-windows -t gsd-phase-ab-verify
tmux capture-pane -pt gsd-phase-ab-verify:commander | tail -n 20
tmux kill-session -t gsd-phase-ab-verify
```

Success means:
- session is created
- all 5 windows exist
- commander window has bootstrapped Hermes and pasted its prompt

## Important implementation findings

### 1. Add `--no-attach`
Without this, script verification is awkward because the script always hijacks the terminal by attaching to tmux.
The launcher should support a non-interactive verification mode.

### 2. Disable tmux auto-rename
Hermes output can cause window names to drift or appear truncated in `tmux list-windows`.
Set these session options after creating the tmux session:

```bash
tmux set-option -t "$SESSION_NAME" allow-rename off
tmux set-option -t "$SESSION_NAME" automatic-rename off
```

### 3. Keep window names short and stable
`verify` worked better than `verifier` because tmux listings can appear clipped and Hermes UI noise makes long names less readable.
Short role labels are better for rapid manager switching.

### 4. Load prompt files via tmux buffer
Reliable bootstrapping pattern:
- start `hermes -w`
- wait a few seconds for startup
- `tmux load-buffer` with the prompt file
- `tmux paste-buffer`
- send Enter

This is more reliable than trying to inline a long quoted prompt directly in `send-keys`.

## Manager operating rule

The user should not supervise every token of every agent.
They should mainly watch:
- current main phase
- which lane is blocked
- the next join point
- whether visible artifacts are actually appearing

That is why the `commander` and `verify` lanes exist separately from implementation lanes.

## Phase A checklist encoded in this setup

The smoke lane must cover these 5 flows:
1. Hermes dashboard home
2. Sessions
3. Config / Env
4. AI Department OS projects
5. approvals decision flow

Each flow should eventually define:
- prerequisites
- steps
- expected result
- failure signal
- regression replay path

## Phase B checklist encoded in this setup

The process-guard lane must formalize:
- spec gate
- plan gate
- execution lane
- review lane
- verification lane

For each, write:
- purpose
- inputs
- outputs
- pass condition
- common failure signals

## Pitfalls

- Do not mix Phase C review personas into this first team bootstrap
- Do not use only one terminal and treat it as "the team"
- Do not skip `-w` when multiple agents may edit in parallel
- Do not rely on a pure web dashboard for multi-agent coordination; tmux is the primary control surface here
- Do not verify the launcher only by reading the script; actually create a throwaway tmux session and inspect windows/pane output
