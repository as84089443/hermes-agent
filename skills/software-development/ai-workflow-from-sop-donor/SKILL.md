---
name: ai-workflow-from-sop-donor
description: Design an AI workflow / operating system by treating an existing SOP system as a governance donor, not as a product shell to copy verbatim.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [workflow, architecture, sop, operating-system, governance, planning]
---

# AI workflow from SOP donor

Use when:
- The user wants to build an AI workflow or operating system around a real business process
- There is an existing SOP repo/system (possibly half-built) that should inform the new design
- The user wants careful design first, not premature implementation
- The old system contains valuable rails but should not be copied blindly

## Core idea

Treat the old SOP system as a **governance donor**.
Do NOT copy its product shell or assume its UI/routes/data layout are the new base app.
Instead, extract:
- decision rails
- state machine logic
- approval / scope-lock rules
- versioning rules
- recurring / project-group logic
- agent boundaries

Then design the new AI workflow around the user’s **actual current business structure**.

## What to extract from the donor

Prioritize these from the SOP donor:
1. PM-driven governance
2. state transitions
3. scope lock and change review
4. exact version / snapshot requirements
5. owner assignment rules
6. human review gates
7. machine-readable contract philosophy

Do NOT inherit blindly:
- old page layout
- old app shell
- old repo boundaries
- stale enum names shown directly to users
- half-finished features just because they already exist

## Design sequence that worked well

Do NOT start by writing many feature specs or UI pages.
Use this sequence:

1. Define product identity
- What is this system actually?
- Usually: a `case operating system`, not a chat app or one-off tool.

2. Write decision rails first
- Human/AI boundaries
- No ownerless case
- No approval without exact version
- No post-lock change without formal review
- AI may assist, not overrule

3. Write the minimal data model
- case as primary object
- sidecars for customer/brand/rules
- historical facts as normalized records, not source of truth

4. Write routing rules
- How new work is classified
- Which lane it enters
- Who owns client / PM / execution
- When to ask the user vs when to trust existing rules

5. Write the state machine
- intake -> clarify -> quote -> confirm -> execute -> deliver -> bill -> close
- include lane-specific booking rules

6. Write phase gates / control points
- exact entry/exit criteria per phase
- lock points
- human gates
- allowed AI actions per phase

7. Only then write playbooks
- intake playbook
- PM playbook
- lane-specific playbooks (wedding, rental, etc.)
- review-and-learning playbook

## Recommended file structure

Keep planning/specs/playbooks/data outputs separate:

```text
docs/
  plans/
    YYYY-MM-DD-workflow-v1.md

  specs/
    workflow-decision-rails.md
    workflow-data-model.md
    workflow-routing-rules.md
    workflow-state-machine.md
    workflow-phase-gates.md
    workflow-file-structure.md

  playbooks/
    intake-playbook.md
    pm-playbook.md
    <lane>-playbook.md
    review-and-learning-playbook.md

exports/
  normalized historical data
  sidecars
  rulebooks
```

Meaning:
- `plans/` = why / overall blueprint
- `specs/` = system rules and structures
- `playbooks/` = how humans and AI operate it
- `exports/` = grounded analysis outputs and local knowledge files

## Sidecar pattern

If the source business data is shared (Sheets, ops docs, finance tables), do NOT pollute it.
Create local sidecars for analysis and AI memory:
- customer sidecar
- brand sidecar
- rulebook / do-not-ask-again file
- normalized history tables

This is essential when:
- multiple humans use the same operational spreadsheet
- the user wants analysis fields but not source-sheet clutter

Practical lesson from real use:
- first read the shared operational tables exactly as they are
- then create a separate local sidecar layer for `owner_guess`, `pm_guess`, brand/system affiliation, confidence, and relationship notes
- never write these analyst-only fields back into the shared ops sheet unless the user explicitly wants that

## Spec completion order that reduced drift

When the design got large, the most effective order was:
1. blueprint / convergence summary
2. decision rails
3. data model
4. routing rules
5. state machine
6. phase gates
7. playbooks
8. machine-readable contract drafts
9. implementation handoff map

This order worked because it delayed implementation details until the governance and object model were stable.

## Add a source-of-truth matrix before implementation

Once multiple specs/playbooks exist, create a short `source-of-truth matrix` that says:
- which file owns each topic
- which files may only reference it
- what to edit first when rules change

Without this, `scope lock`, `change review`, `do-not-ask-again`, and sidecar rules tend to drift across documents.

## Add an explicit v1 / v1.1 boundary

Before building, write down what is intentionally deferred.
Examples of things that often belong in v1.1 rather than v1:
- `operating_controller` as a first-class field
- `upstream_source` as a first-class field
- lane-specific recap schemas
- recurring sidecars
- full UI and machine-readable contract execution

This prevents accidental scope creep during implementation.

## Bridge planning to implementation explicitly

Before coding, create an `implementation handoff map` that links:
- spec -> contract
- contract -> module
- module -> UI
- v1 build order

For this kind of workflow system, the most stable implementation order was:
1. case repository core
2. sidecar resolver
3. routing engine
4. intake normalizer
5. review recap writer
6. minimal dashboard / cases / case detail

## What the workflow must model explicitly

At minimum, define these separately:
- client owner
- PM owner
- whether the principal personally executes
- role in execution (main output / support / management / not involved)
- lane
- current owner
- next action / next owner
- quote version / artifact version

Do not rely only on split ratios, project names, or vague labels.

## Review-and-learning is mandatory

The system does not actually learn unless every completed case produces:
1. case recap
2. rule update suggestion
3. reusable asset suggestion
4. sidecar / rulebook updates when needed

Important durable rule:
- if the user has already confirmed a client/brand/case line multiple times, it must go into a `do-not-ask-again` mechanism

## Good design heuristics

- Use the smallest question that reduces uncertainty
- Preserve partial truth; do not force full structured answers every time
- Build rules from the user’s own language
- Keep lane-specific logic separate where the business reality truly differs
- Make completed phases visibly usable, not just internally “done”

## Pitfalls

- Writing a giant PM playbook before defining phase gates
- Letting the donor system dictate the new product shell
- Mixing source data with analyst-only fields
- Treating AI as an autonomous operator instead of a rails-bound assistant
- Confusing historical normalized facts with canonical workflow schema

## Done when

You have:
- one clear system identity
- donor rails extracted and translated
- specs written before playbooks sprawl
- a clean file structure
- lane-aware playbooks
- a learning loop that prevents repeated questioning
