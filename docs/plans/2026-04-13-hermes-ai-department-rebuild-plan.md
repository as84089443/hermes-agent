# Hermes AI Department Rebuild Plan

Date: 2026-04-13

> For Hermes: use this as the canonical implementation plan for rebuilding the AI department as a single product instead of extending scattered unfinished systems.

Goal:
Build a single AI Department OS that turns a brief into a tracked, reviewable, publish-ready video work package.

Architecture:
Use one canonical app shell with one project state model, one handoff contract, one approval queue, and one artifact schema. Treat existing repos as reference material and migration sources only.

Tech stack:
Next.js + TypeScript + one database layer + Hermes orchestration + wiki/memory artifact capture.

---

## Task 1: Freeze the canonical product boundary

Objective:
Decide the new system is one product with modules, not multiple peer apps.

Files:
- Create: `docs/plans/2026-04-13-hermes-ai-department-rebuild-plan.md`
- Modify: `docs/plans/2026-04-13-multi-department-agent-operating-model.md`
- Modify: `docs/plans/2026-04-13-ai-video-department-architecture.md`

Step 1: Add one decision block to both architecture docs

Required decision:
- canonical product = single AI Department OS
- old repos = references, not required inheritance targets
- v1 scope = video department only

Step 2: Verify both docs now agree on the same target shape

Run:
- `rg -n "single AI Department OS|references, not required inheritance" docs/plans`

Expected:
- matching statements in both files

Step 3: Commit

Suggested commit:
- `docs: align ai department around single-product rebuild`

---

## Task 2: Define the canonical state model

Objective:
Create separate but linked state machines for Project, Task, Handoff, Approval, and Artifact.

Files:
- Create: `docs/specs/ai-department-state-machine.md`
- Create: `docs/specs/ai-department-data-model.md`

Step 1: Write the project state list

Required states:
- intake
- triage
- in_progress
- review
- revise
- approval_pending
- publish_pack_ready
- completed
- archived

Side states:
- blocked
- canceled

Step 2: Write the task / handoff / approval / artifact states

Required task states:
- queued
- in_progress
- review
- needs_revision
- done
- blocked
- canceled

Required handoff states:
- drafted
- sent
- accepted
- rejected

Required approval states:
- pending
- approved
- changes_requested
- rejected

Required artifact states:
- draft
- final
- superseded

Step 3: Write transition rules

Include:
- who can move each state
- which transitions require approval
- what artifact must exist before transition
- every transition must emit an Event row

Step 4: Write core entities

Required entities:
- Project
- Task
- Handoff
- Approval
- Artifact
- Event

Step 5: Verification

Review each entity and make sure every field supports either routing, auditability, or output packaging.
Also verify:
- every approval points to exact artifact versions
- every handoff can be accepted or rejected by the next owner
- no project field duplicates canonical brief content unnecessarily

---

## Task 3: Define the artifact contract

Objective:
Make every pilot output predictable and machine-readable.

Files:
- Create: `docs/specs/ai-video-artifact-contract.md`
- Create: `docs/templates/brief.md`
- Create: `docs/templates/handoff.yaml`
- Create: `docs/templates/qa-gate.md`
- Create: `docs/templates/publish-pack.md`
- Create: `docs/templates/retro.md`

Step 1: Define required artifact list

Required files:
- `brief.md`
- `research.md`
- `strategy.md`
- `script.md`
- `storyboard.md`
- `prompt-pack.md`
- `asset-checklist.md`
- `edit-plan.md`
- `qa-report.md`
- `publish-pack.md`
- `retro.md`

Step 2: Make all templates concrete

Every template must include:
- required fields
- owner
- status
- next action

Step 3: Verification

Run a manual pass:
- could a new project be created with zero improvisation?
- can each artifact hand off cleanly to the next role?

---

## Task 4: Define the worker roster for v1

Objective:
Lock the smallest useful set of workers.

Files:
- Create: `docs/specs/ai-department-worker-roster.md`

Step 1: Define only these workers
- intake-normalizer
- research
- script
- storyboard
- qa-compliance
- publish-packager
- analytics-learning

Step 2: For each worker, write:
- purpose
- accepted inputs
- required outputs
- allowed side effects
- escalation conditions

Step 3: Verification

Check:
- no worker has overlapping authority
- every worker produces one primary artifact type
- every worker names the next owner explicitly

---

## Task 5: Design the command center surface

Objective:
Specify the first UI without implementing the whole app.

Files:
- Create: `docs/specs/ai-department-command-center.md`

Step 1: Define only two required screens
- `/projects`
- `/projects/[id]`

Step 2: `/projects` must show
- project title
- status
- current owner
- next gate
- risk level
- deadline

Step 3: `/projects/[id]` must show
- canonical artifact list
- handoff history
- approval queue
- next recommended action

Step 4: Verification

Ask of the spec:
- can an operator know what is blocked in under 10 seconds?
- can a human approve or reject without opening five pages?

---

## Task 6: Connect Hermes to the rebuild model

Objective:
Turn Hermes into the orchestration engine rather than a loose helper.

Files:
- Create: `docs/specs/hermes-orchestration-integration.md`

Step 1: Define Hermes responsibilities
- normalize brief
- create execution graph
- launch role-specific runs
- write artifacts
- update wiki/memory
- schedule retros and follow-ups

Step 2: Define tool usage by role
- file
- terminal
- delegate_task
- cronjob
- memory
- session_search

Step 3: Define human gates
- brand strategy
- legal / rights
- sensitive claims
- final publish

Step 4: Add subagent parallel execution fabric spec
- Create: `docs/specs/subagent-parallel-execution-fabric.md`
- Define which roles can run in parallel
- Define join points and merge owners
- Define peer review, gate review, and escalation review
- Define branch-aware event logging requirements

Step 5: Verification

Confirm that Hermes is responsible for coordination, not hidden business logic locked inside prompts.
Confirm that multi-agent parallelism still leaves a complete audit trail.

---

## Task 7: Run one pilot end-to-end on paper

Objective:
Test the design before coding the product.

Files:
- Create: `docs/pilots/ai-video-pilot-001.md`

Step 1: Pick one narrow pilot
- one platform
- one CTA
- one language
- one review gate

Step 2: Fill every artifact template
- brief
- script
- storyboard
- QA
- publish pack
- retro

Step 3: Verification

If any field is invented ad hoc during the dry run, update the schema before coding.

---

## Task 8: Build only after the paper pilot passes

Objective:
Prevent building the wrong product.

Files:
- Future implementation repo or app directory to be chosen after the paper pilot

Step 1: Do not code before Tasks 1-7 are stable
Step 2: Convert the validated schemas into DB models and UI screens
Step 3: Implement only `/projects` and `/projects/[id]` first
Step 4: Add one worker at a time

Verification:
- first code milestone is a tracked project moving from intake to QA
- not a broad dashboard with no real state discipline

---

## Completion criteria

This rebuild plan is ready for implementation when:
- the canonical product boundary is written down
- the state model is fixed
- artifact templates are fixed
- worker roster is fixed
- command center spec is fixed
- one pilot dry run has exposed and closed the schema gaps
