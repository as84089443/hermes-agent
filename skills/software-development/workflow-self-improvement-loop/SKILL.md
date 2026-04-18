---
name: workflow-self-improvement-loop
description: Design a self-improving workflow/agent operating system without prematurely jumping to prompt evolution or code self-modification.
---

# Workflow Self-Improvement Loop

Use this when building an AI workflow / agent OS that must learn from real tasks, reduce repeated clarification, and accumulate reusable business rules.

This skill is especially useful when the team is tempted to jump straight into GEPA/DSPy/prompt optimization before the operational workflow is stable.

## Core Insight

Separate two layers:

1. Workflow self-improvement
- Learns the business/world model
- Examples: customer ownership, PM ownership, execution role, brand routing, do-not-ask-again rules
- Triggered by live case events

2. Agent self-evolution
- Optimizes skills, prompts, tool descriptions, or code
- Examples: DSPy/GEPA optimization of routing prompts or skill text
- Should happen only after the workflow loop is stable and measurable

Do NOT start with layer 2.

## Recommended Order

### Phase A — Make the workflow learning loop real
Build these in order:
1. Case repository
2. Sidecar resolver
3. Routing engine
4. Review recap writer
5. Do-not-ask candidate detector
6. Routing mismatch tracker

Goal: the system can take in work, classify it, capture corrections, and write back learning suggestions.

### Phase B — Add metrics
Minimum metrics:
- routing correction rate
- repeated clarification count
- do-not-ask hit rate
- recap pending rate

Helpful extras:
- customer sidecar hit rate
- brand sidecar hit rate
- sidecar confidence promotion rate
- rulebook writeback rate
- high-value mismatch pool size

Goal: know whether the system is actually learning, not just storing data.

### Phase C — Only then add offline evolution
Only after A+B are stable, use an external optimizer (like Hermes Agent Self-Evolution) on ONE target first:
- routing prompt / heuristic text

Do not start by optimizing every skill or prompt in the system.

## Red / Blue Test Framework

### Blue Tests (must be mostly true before Phase C)
- Known customer lines stop being re-asked
- Cases can close with recap consistently
- Routing mismatches are logged with root-cause guesses
- Repeated clarification becomes do-not-ask candidates
- Metrics show improvement over time

### Red Tests (if true, do NOT start prompt evolution yet)
- Routing still needs heavy human correction
- Sidecar and rulebook often contradict each other
- Do-not-ask rules still fail in practice
- Recaps frequently lack core fields
- Core schema is still changing often

## Memory Architecture

Use three layers:

### Working memory
Current case/session context only.
Examples:
- current case draft
- pending clarification
- next action

### Episodic memory
Specific event records.
Examples:
- review recap
- change review record
- routing mismatch record
- one-off correction note

### Semantic memory
Stable reusable knowledge.
Examples:
- customer sidecar
- brand sidecar
- analysis rulebook
- do-not-ask-again
- stable routing rules

Rule: do not promote working/episodic data directly into high-confidence semantic rules without validation.

## Critical Design Rules

1. Do not auto-upgrade uncertain business facts to high confidence.
2. Do not let AI finalize client_owner / pm_owner / execution-role without human confirmation.
3. Route learning outputs into the correct target:
   - customer sidecar
   - brand sidecar
   - rulebook
   - do-not-ask list
   - playbook/spec update candidate
4. Use mismatch records as the bridge from live operations to future prompt optimization.
5. Build source-of-truth hierarchy early so knowledge does not drift across files.

## Minimal Artifacts to Define

Human-readable specs:
- decision rails
- data model
- routing rules
- state machine
- phase gates
- review recap schema
- self-improvement loop spec
- metrics schema
- source-of-truth matrix
- v1/v1.1 boundary

Machine-readable contracts:
- case schema
- sidecar schema
- recap schema
- mismatch schema
- metrics schema

## When to Use Official Self-Evolution Repo

Use Hermes Agent Self-Evolution only after:
- workflow loop is running end-to-end
- recap and mismatch data are clean enough
- metrics are being tracked
- one optimization target is clearly defined

Best first target:
- routing prompt / heuristic text

## Common Failure Modes

- Starting with prompt evolution before workflow rules are stable
- Treating all chats as long-term memory
- No confidence tracking on promoted rules
- No do-not-ask mechanism
- No recap requirement before close
- Letting UI design drive workflow rules

## Practical Heuristic

If the system still frequently asks the operator to repeat known business context, you are still in Phase A. Do not move to DSPy/GEPA yet.
