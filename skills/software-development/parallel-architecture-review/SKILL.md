---
name: parallel-architecture-review
description: Use when designing or rebuilding a complex system architecture and you want faster, higher-quality convergence by running multiple subagents in parallel on different review angles, then merging their findings into one canonical blueprint.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, planning, delegation, subagent, parallel, review]
    related_skills: [writing-plans, subagent-driven-development, systematic-debugging]
---

# Parallel Architecture Review

Use this when:
- Rebuilding a product or system from scratch
- Reviewing a large architecture or operating-model document set
- Migrating from fragmented legacy systems to one canonical design
- The user wants multi-agent parallel work instead of one long serial analysis

Core idea:
Run 2-3 subagents in parallel, each focused on a different architecture dimension, then merge only the concrete findings back into the canonical blueprint and plan.

## Best review split

For a product/agent-system rebuild, use these three lanes:

1. Data model + state machine
- Find minimal entities
- Separate project/task/handoff/approval/artifact/event concerns
- Remove mixed state models
- Add auditability requirements

2. Execution fabric + concurrency
- Define what can run in parallel vs serial
- Specify join points, merge owners, review loops, escalation rules
- Model subagent-first execution, not just hub-and-spoke

3. Product shell + migration policy
- Shrink v1 UI surfaces to the minimum
- Decide which legacy systems are donors vs discard
- Define schema-first, slice-based migration rules

### Special case: self-advancing project systems

When the user asks for a system that can keep pushing projects forward autonomously, split the review into these three concrete lanes instead of staying abstract:

1. Persisted control-plane lane
- Verify whether the current system has real project-level state, not just session/chat history
- Check for canonical persisted fields like `main_phase`, `next_action`, typed blockers, artifact refs, review/approval state, and append-only events
- Explicitly distinguish transcript-derived heuristics from machine-written state

2. Re-entry runtime lane
- Verify whether cron/scheduler/background workers can do `read state -> choose next action -> act -> write state`
- Look for the exact missing glue between existing runtime primitives and project advancement
- Prefer a one-step-per-tick autopilot loop with noop guards over long free-running loops

3. Boss-mode shell lane
- Verify whether the front door is project-centric or merely session-centric
- Separate visible status that is grounded in real ledger rows from status inferred from markdown or chat summaries
- Recommend the smallest viable shell first: `/projects`, `/projects/[id]`, `/approvals`, `/settings`

For this special case, make the child reviewers return:
- what already exists and can be reused as-is
- what is fake/manual/heuristic today
- the minimal persisted entities required for autonomy
- the minimal autopilot loop
- the minimal operator UI/control surface

## Controller workflow

1. Prepare the canonical docs
- Read the main blueprint
- Read the operating model / agent map
- Read the implementation plan
- Read any ecosystem inventory or legacy-system summary

2. Launch parallel subagents
Use `delegate_task(tasks=[...])` with one task per lane.
Each task should:
- read only the relevant files
- return concrete patches, not vague commentary
- optimize for v1 minimalism and auditability

3. Ask each subagent for the same output shape
Preferred format:
- Findings
- Concrete patches
- Risks / over-design warnings

4. Merge only durable conclusions
Patch the canonical docs with:
- narrowed v1 scope
- explicit state models
- exact handoff schema
- event logging rules
- donor vs base-app policy
- parallel execution rules

5. Update navigation artifacts
If using a wiki:
- update index
- update topic map / control page
- append log entry

## Good prompt pattern for child agents

Pass this structure:
- Files to read
- Exact goal
- Hard constraints
- Output format

Example constraints:
- Assume one-product rebuild
- Optimize for v1 minimal scope
- Emphasize auditability and structured handoff
- Avoid generic advice

## Merge heuristics

Prefer findings that:
- reduce duplicated state
- reduce UI surface area
- make handoffs accept/reject-able
- require event logs for important transitions
- keep legacy systems as donors rather than inherited shells
- preserve human gates for risky decisions
- import strong decision rails from half-built systems without inheriting their whole product shell
- preserve "freeform intake first, then 2-4 follow-up questions" when the old system proved structured forms were too heavy
- encode scope lock / change review / version snapshot rules explicitly
- use visible operator workflows as acceptance criteria, not invisible internal checklist completion

Reject findings that:
- add extra dashboards for v1
- mix approval states into project states
- duplicate brief content across project rows and artifacts
- assume serial execution when parallel specialists are clearly viable
- copy old repo boundaries wholesale just because the prior system already exists

## Importing decision rails from unfinished legacy systems

When the user provides a half-built system, SOP pack, or project-memory document, do not treat it as a base app to inherit blindly.

Instead, extract and merge only the durable operating rules:
- what must lock after a milestone (`scope lock`)
- what changes require formal review (`change review`)
- what must always be versioned and snapshotted
- where humans must remain in the loop
- what acceptance standard the user actually wants (for example, visible working pages instead of checklist signoff)

Good examples of reusable rails:
- freeform intake before structured forms
- explicit owner assignment early in the lifecycle
- no agent action outside contract / rails
- no approval without exact artifact version
- phase-based visible delivery review

Then patch the new canonical blueprint and pilot docs with those rails, while keeping the legacy repo in donor/reference status.

## Canonical patches commonly worth making

- Split state machines by entity type instead of one shared lifecycle
- Add explicit `Event` schema
- Add handoff acceptance fields (`accepted_by`, `accepted_at`, status)
- Narrow v1 UI to command center, project workspace, approvals, settings
- Treat old repos as read-only donors during v1
- Replace "task sequence" language with "execution graph" when subagents run in parallel

## Reusable design lesson: workflow systems should be written in layers

When designing an AI operating system or case/workflow platform from messy real operations, do not jump straight into a giant PM playbook or UI spec.
A better order that emerged in practice is:

1. `decision rails`
- define what AI may do, what requires human approval, what locks after confirmation, and what cannot change without review

2. `data model`
- define the smallest stable entities and fields needed for routing and auditability
- especially owner, PM, executor, brand/system, version, and next-action fields

3. `routing rules`
- define how new work is classified into lanes and how ownership is inferred
- prefer explicit source-of-truth signals over title heuristics

4. `state machine`
- define entry/exit criteria for each phase, including lock points and change-review triggers

5. `playbooks`
- only after the above are stable, write operator-facing playbooks (intake, PM, delivery, etc.)

Why this order matters:
- without rails, playbooks drift into unchecked AI behavior
- without the data model, routing rules become hand-wavy
- without routing rules, the state machine becomes generic and ungrounded
- without phase gates, PM playbooks become long essays instead of executable control logic

A useful extra document between `state machine` and `playbooks` is a `phase gates` or `control points` spec that defines exactly what must be true before a case can move to the next stage.

## After the review converges: scaffold the v1 shell immediately

Once the blueprint is stable enough, do not stop at documents if the user wants execution.

Recommended follow-up pattern:

1. Launch another parallel pass for implementation bootstrap
- One subagent designs the minimal repo scaffold and page/route tree
- One subagent designs the machine-readable contracts and minimal data model
- Optionally a third subagent reviews donor-vs-base-app migration choices

2. Materialize a real product shell right away
Create the smallest runnable repo that includes:
- app shell
- `/projects`
- `/projects/[id]`
- `/approvals`
- `/settings`
- placeholder API routes for intake, projects, tasks, handoffs, approvals, artifacts, events, and orchestration
- copied specs/contracts/templates inside the new repo

3. Prefer mock data first for visible delivery
Before wiring full persistence, make the pages visibly usable with mock or seed data so the user can inspect real surfaces instead of more planning text.

4. Verify with actual build steps
Run the real install/build/typecheck commands and confirm the shell compiles. A successful scaffold should be grounded by tool output, not just by file creation.

This pattern is especially useful when the user prefers phase-based visible delivery and wants a working front door before deeper backend work.

## Pitfalls

- Letting subagents return essays instead of patches
- Keeping too many legacy routes alive in v1
- Failing to define merge/join ownership for parallel branches
- Mixing project state with task or approval state
- Forgetting to update wiki indices and logs after patching

## Verification

Before stopping, confirm:
- v1 UI is minimal
- state models are explicit and non-overlapping
- parallel vs serial rules are written down
- every important transition can be audited
- human gates still exist for high-risk decisions
- canonical docs agree with each other
