---
name: workflow-design-from-messy-operational-data
description: Build a practical operating-system/workflow architecture from messy real-world business data by separating facts, inferred rules, sidecars, and governance docs before implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [workflow, operations, architecture, sidecar, normalization, planning]
---

# Workflow design from messy operational data

Use this when:
- The user wants an AI workflow / operating system built from messy real-world business data
- Inputs are scattered across calendars, spreadsheets, chats, and memory
- Shared source tables cannot be polluted with analysis-only columns
- The user keeps correcting business logic (customer ownership, PM ownership, role attribution)
- You need to turn historical behavior into a clean workflow architecture before implementation

## Core idea

Do NOT jump straight to product or automation.
First separate:
1. Facts
2. Inferred rules
3. Shared operational tables
4. Private sidecars / rulebooks
5. Governance docs
6. Implementation bridge

The reusable pattern is:
- normalize messy history
- ask only high-value clarifying questions
- store durable rules outside shared source tables
- stop repeating questions by building a do-not-ask layer
- derive architecture from real business structure, not generic SaaS assumptions

## Best workflow

### Phase 1 — Build the factual base

1. Export the relevant operational history
- calendars
- income / payout spreadsheets
- customer/vendor tables
- any existing notes / donor SOP docs

3. Normalize into one analyzable table
Minimum useful columns:
- date
- case title
- source sheet/calendar
- gross income
- net to each participant
- raw vendor/customer text
- raw notes / support text

IMPORTANT learned in practice:
- If the shared income sheet already has a dedicated vendor/customer column, treat that column as a higher-confidence anchor than the freeform case title.
- Build alias maps from that vendor column into the customer/brand sidecars before asking the user many more classification questions.
- Expect some rows to have vendor='-' or blank; those should be prioritized for user clarification because automated matching will stall there.

4. Keep raw exports immutable
Write normalized outputs to separate files under an exports/ directory.
Do not rewrite the source spreadsheets unless explicitly asked.

## Phase 2 — Separate analysis from shared operations

If the original sheet is shared by multiple people:
- do NOT add speculative fields directly into it
- instead create local/private sidecars

Create:
1. customer sidecar
2. brand sidecar
3. rulebook
4. do-not-ask list

### Customer sidecar should hold
- customer_name
- aliases
- owner_guess
- pm_guess
- relationship_type
- confidence
- notes
- do_not_ask_again

### Brand sidecar should hold
- brand_name
- aliases
- owner_type_guess
- pm_owner_guess
- default_lane
- operating_note
- confidence

### Rulebook should hold
- stable routing rules learned from user corrections
- examples of common case types
- explicit “do not re-ask” rules

## Phase 3 — Clarify only the highest-value ambiguity

Do not ask about everything.
Ask only what most reduces future uncertainty.

Good order:
1. Customer ownership
2. PM ownership
3. Whether the principal person actually executed
4. Whether the case belongs to a brand/system line
5. Whether the case is active income vs passive income

### Ask in batches of 5 max
Especially for long historical cleanup, the user may hate scrolling.
Keep each batch small.

### Let the user answer partially
If the user only remembers one dimension (for example “this is my client”), store that and leave the rest pending.
Do NOT force complete classification in one go.

## Phase 4 — Convert repeated answers into rules

When the user repeats a pattern, stop asking it case-by-case.
Turn it into a rule.

Examples of reusable rules discovered in practice:
- If a customer is Brian’s customer, PM often defaults to Brian unless a clear exception exists.
- If Brian and Jerry income are close, many cases should default to shared-customer / shared-PM.
- Wedding sub-brand work may be jointly owned but operationally controlled by another person (for example Chu).
- Studio rental is passive/asset income and must be separated from active execution income.

Any case line confirmed multiple times should move into:
- sidecar
- rulebook
- do-not-ask-again list

## Phase 5 — Build the architecture from reality, not theory

Once you have enough normalized facts and rules, define the workflow as an operating system.

Recommended doc stack:

### Plans
- blueprint / overall design
- design convergence summary

### Specs
- decision rails
- data model
- routing rules
- state machine
- phase gates
- file structure
- sidecar schema
- recap schema
- source-of-truth matrix
- v1 vs v1.1 boundary
- implementation handoff map

### Playbooks
- intake
- PM
- lane-specific playbooks (wedding, studio rental, etc.)
- review and learning

### Contracts
Start with minimal machine-readable contracts for:
- case schema
- customer/brand sidecar schema
- review recap schema

## Phase 6 — Keep governance separate from implementation

When there is an unfinished donor system (for example BW-SOP), do not clone it wholesale.
Extract its durable governance:
- state machine
- owner rules
- booking / confirmation rules
- scope lock
- change review
- version snapshots
- AI non-overreach rules

Then adapt those rails to the user’s real business structure.

## Phase 7 — Prevent planning sprawl

Once you have enough documents, stop adding more broad planning docs.
Do a design convergence pass and produce:
1. source-of-truth matrix
2. v1 / v1.1 boundary
3. implementation handoff map

That is the signal to stop expanding planning and start minimal implementation.

## Phase 8 — Bridge into implementation carefully

Before implementing, inspect the existing repo's persistence and module patterns first.
Do not invent a new storage style blindly.

### Add one final bridge before coding
When the planning set becomes large enough, add three explicit bridge docs before implementation:
1. source-of-truth matrix
2. v1 / v1.1 boundary
3. implementation handoff map

These three documents are the signal to stop writing broad planning docs and start narrowing into repository-first implementation.

Reusable implementation lessons:
- check how the repo already does profile-aware paths (`get_hermes_home()` or equivalent)
- check how the repo already uses SQLite / row factories / WAL / schema bootstrap
- prefer a small dedicated module for the new workflow domain rather than forcing it into an unrelated existing store
- keep the first implementation slice narrow: repository core before API/UI

A good first implementation slice is often:
1. models
2. validation
3. state-machine / transition guard
4. storage layer
5. repository

Then add:
6. sidecar resolver
7. routing engine
8. review recap writer
9. do-not-ask candidate detector
10. routing mismatch tracker
11. metrics aggregator
12. API adapter
13. UI adapter

This sequencing worked well in practice because it let the workflow learn before UI complexity or offline optimizers were introduced.
It also reduces the risk of repeatedly asking the user already-settled questions.

Practical implementation lesson:
- after each major planning pass, do a convergence step and stop expanding specs
- then implement the core in this order: repository → resolver → routing → recap → do-not-ask → mismatch → metrics
- only after those are stable should you consider plugging in an offline self-evolution optimizer (e.g. DSPy/GEPA) to improve routing prompts or heuristics

## Phase 9 — Formalize the self-improvement loop

Once case / sidecar / recap contracts exist, explicitly define how the system learns.
Do not leave “self-improvement” as a vague aspiration.

Use three memory layers:
1. working memory — current case/session context
2. episodic memory — recap, mismatch, change-review records
3. semantic memory — sidecars, rulebook, do-not-ask-again, stable routing rules

Most valuable learning triggers:
- case close
- change review
- routing mismatch
- repeated clarification
- recurring high-value pattern

Important rule:
- AI may recommend writebacks, but human must confirm high-impact fields like client_owner, pm_owner, brian_exec, brian_role, income_nature, and do-not-ask-again promotion.

Good first self-improvement modules are:
1. review recap writer
2. sidecar update recommender
3. do-not-ask candidate detector
4. routing mismatch tracker
5. workflow metrics aggregator

A practical order that worked well in implementation:
- case repository
- sidecar resolver
- routing engine
- review recap writer
- do-not-ask candidate detector
- routing mismatch tracker
- workflow metrics aggregator

Do not jump to an offline optimizer until those core modules exist and pass real tests.

### Important distinction: workflow learning vs offline optimizer
A useful architectural split emerged in practice:

- Workflow self-improvement (inside the business OS)
  - Learns from real cases, corrections, recap records, and repeated clarifications
  - Writes back to sidecars, rulebooks, do-not-ask-again lists, and recurring templates
  - Optimizes operating intelligence: ownership, PM routing, execution role, brand/system classification

- Offline self-evolution repo / optimizer
  - Evolves skills, prompts, tool descriptions, or code in batch runs
  - Uses datasets, evaluators, fitness metrics, constraint gates, and human-reviewed promotion
  - Optimizes agent capability, not day-to-day business truth

Recommended order:
1. Stabilize workflow self-improvement first (case → recap → sidecar/rulebook loop)
2. Define metrics (routing correction rate, repeated clarification count, do-not-ask hit rate, recap pending ratio)
3. Only then connect an offline optimizer to improve prompts/skills using the accumulated recap/mismatch data as evaluation input

### Add explicit red/blue tests before adopting the offline optimizer
Do not integrate an external self-evolution repo just because it looks powerful. First run readiness tests.

Blue tests (must mostly pass):
- known customer/brand lines stop being re-asked
- every closed case can emit a recap with final owner/PM/execution/income fields
- routing mismatches are captured as structured episodes
- repeated clarification can produce do-not-ask candidates
- metrics trend in the right direction over multiple batches

Red tests (if these still dominate, pause offline evolution work):
- routing still depends on heavy manual correction
- sidecar / rulebook frequently contradict each other
- do-not-ask rules do not actually reduce repeated questions
- recap records often leave core fields pending
- schemas are still changing too often

### Add one bridge layer before implementation
Before coding, add three explicit bridge docs once planning becomes large enough:
1. source-of-truth matrix
2. v1 / v1.1 boundary
3. implementation handoff map

These documents are what stop a large workflow design from turning into blind modifications.

## Heuristics that worked well

### Good
- Use sidecars instead of changing shared source sheets
- Treat “facts” and “rules” as separate layers
- Use the user’s corrections to promote low-confidence rows into medium/high confidence
- Maintain a do-not-ask-again list explicitly
- Use donor systems for governance, not as mandatory product shells
- Build lane-specific playbooks only after the common rails are stable

### Bad
- Asking the user to fully classify every historical record
- Re-asking already-settled customer lines
- Using split ratios alone to infer ownership/PM
- Mixing passive income with active execution income
- Letting UI decisions drive rules before the rules are written
- Polluting shared operational spreadsheets with speculative analysis columns

## Suggested file/output pattern

```text
exports/
  normalized-history-vN.json
  customer-sidecar-vN.json
  brand-sidecar-vN.json
  analysis-rulebook-vN.json

docs/plans/
  workflow-v1.md
  workflow-design-convergence.md

docs/specs/
  workflow-decision-rails.md
  workflow-data-model.md
  workflow-routing-rules.md
  workflow-state-machine.md
  workflow-phase-gates.md
  workflow-source-of-truth-matrix.md
  workflow-v1-v1_1-boundary.md
  workflow-implementation-handoff-map.md

docs/playbooks/
  intake-playbook.md
  pm-playbook.md
  review-and-learning-playbook.md
  lane-specific-playbook.md

docs/contracts/<workflow>/
  case.schema.json
  customer-brand-sidecar.schema.json
  review-recap.schema.json
```

## Done when
- historical data is normalized
- sidecars exist and are separate from shared source tables
- repeated user corrections have been encoded into rules
- a do-not-ask-again list exists
- the workflow has rails, schema, routing, state, and recap defined
- v1 vs v1.1 boundaries are explicit
- there is a clear handoff path from planning to implementation
