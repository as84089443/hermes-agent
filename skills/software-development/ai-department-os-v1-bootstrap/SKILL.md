---
name: ai-department-os-v1-bootstrap
description: Bootstrap or extend the ai-department-os v1 as a single-product AI department system with JSON-backed repositories first, Telegram bridge preparation, and visible operator-facing pages before heavier infrastructure.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-department, nextjs, bootstrap, telegram, json-repository, project-specific]
---

# AI Department OS v1 Bootstrap

Use when working on `/Users/brian/dev/ai-department-os` or rebuilding the user's AI department system.

## When to use
- User wants to continue building the AI department OS
- Need to scaffold or extend the v1 product quickly
- Need a visible working phase before deeper infra
- Need Telegram integration without immediately cutting over the existing production webhook

## Core approach
1. Treat this as a **single-product rebuild**, not an extension of scattered legacy repos.
2. Start with a **JSON-backed repository layer** and repository abstraction.
3. Make `/projects`, `/projects/[id]`, and `/approvals` visibly usable before deeper automation.
4. Prepare Telegram bridge safely, but do **not** assume polling is available if a webhook already exists.
5. Defer Prisma/Supabase as the primary runtime store until the v1 entity/API shapes stabilize.

## Canonical v1 surfaces
- `/projects` — command center
- `/projects/[id]` — one-page workspace
- `/approvals` — human gate queue
- `/settings` — rails / brand / risk config

## Recommended implementation order

### Phase 1: Lock schema and repository boundary
Create or maintain:
- `lib/domain/enums.ts`
- `lib/domain/types.ts`
- `lib/domain/validators.ts`
- `lib/server/store.ts`
- `lib/server/repositories.ts`

Persist these entities first:
- Project
- Task
- Handoff
- Approval
- Artifact
- Event

Use per-project JSON files under:
- `data/projects/<projectId>/project.json`
- `tasks.json`
- `handoffs.json`
- `approvals.json`
- `artifacts.json`
- `events.json`

Important rule:
- `nextGate` and `waitingOnHuman` should be **derived**, not source-of-truth persisted fields.

### Phase 2: Make the operator pages real
Replace mock data with repository-backed reads/writes:
- `/projects` should create real projects and show live approval snapshot
- `/projects/[id]` should support:
  - updating project rails
  - creating tasks
  - creating artifacts
  - creating handoffs
  - requesting approvals
- `/approvals` should support approval decisions

Prefer server actions for the first visible operating loop.

### Phase 2.5: If the user is reviewing from mobile, optimize for decision readability first
Important experiential finding:
- A mobile-accessible preview URL alone is NOT enough.
- If the page still shows long raw text blocks, internal labels, and dense admin-console layout, the user will correctly feel that the system has no visible value yet.

For mobile-first review rounds, do this before adding more backend shape:
- make the UI default to Traditional Chinese if that is the user's product language
- surface 3 top summary cards on `/projects/[id]`:
  - current direction
  - current blocker
  - next decision
- make long project documents collapsible behind `details/summary` or equivalent
- turn `/approvals` into decision cards that explicitly answer:
  - what am I deciding?
  - what happens if I approve?
  - where does it go if I reject?
- avoid defaulting the decision selector to `approved`; use a safer default such as `changes_requested`

Controller rule:
- When the user says they still "can't see the effect" or the app feels like "a bunch of text," stop adding contracts and restructure the visible operator flow instead.

### Phase 3: Event discipline
Every write operation should append an event:
- `project_created`
- `project_updated`
- `project_state_changed`
- `task_created`
- `task_state_changed`
- `handoff_sent`
- `handoff_accepted`
- `approval_requested`
- `approval_decided`
- `artifact_written`

### Phase 4: Telegram bridge preparation
Implement:
- `lib/telegram/config.ts`
- `lib/telegram/types.ts`
- `lib/telegram/client.ts`
- `lib/telegram/auth.ts`
- `lib/telegram/handler.ts`
- `app/api/telegram/webhook/route.ts`
- `scripts/telegram-check.mjs`
- `scripts/telegram-polling.mjs`
- `app/api/approval-queue/route.ts`

Minimum commands:
- `/help`
- `/status`
- `/approvals`
- `/intake <brief>`

## Founder / executive operating lens for this project
When extending ai-department-os for this user, do not treat it as a generic project tracker. It should embody a founder-style operating system for an AI video company.

## Canonical four-layer donor integration rule
For future work on this project, treat these four donor layers as the default operating stack:
- GSD = verification layer (browser QA, regression, mobile/operator smoke tests, visual diff, authenticated flow checks)
- Superpowers = execution-discipline layer (spec, plan, execute, review, verify)
- gstack = decision/review layer (founder, design, eng, QA, retro/learn personas)
- SuperClaude = command/component layer (command taxonomy, personas/modes, MCP bundles, operator presets)

Default controller behavior:
- For any visible UI or operator workflow, ask what the GSD verification lane is.
- For any multi-step implementation, explicitly structure it as spec → plan → execute → review → verify.
- For any approval, quality bar, or high-risk decision, assign the relevant review persona instead of treating it as generic CRUD.
- For any operator-facing capability, think about command taxonomy / mode / preset design instead of only raw feature implementation.

Apply these lenses during planning and implementation:
- **Exception-driven management**: prioritize what needs a decision, what is blocked, and what is high-risk over showing raw workflow detail first
- **Single-threaded owner**: every project, task, handoff, and approval should make the current owner obvious
- **Quality-bar gates**: direction lock, publish readiness, risky claims, and major revisions should become explicit gates
- **Product taste over admin-console sprawl**: operator-facing UI should answer "what is happening / what is blocked / what needs approval next" before exposing internals

Concrete implications:
- `/projects` and `/projects/[id]` should surface exception summaries first, not raw logs
- `/approvals` should explain why the decision matters now and what changes after approval/rejection
- accepted handoffs should be treated as an ownership transfer, not just a status update
- once direction/scope is locked, later changes should automatically consider stricter change-review behavior

## Critical finding about Telegram
Before using polling, ALWAYS check whether the bot already has an active webhook.

Observed reusable pattern:
- `getUpdates` can return `409 Conflict` if Telegram already has a webhook configured.
- In this case, do **not** assume polling is the right next step.
- First check `getWebhookInfo`.
- If a webhook already points to an existing production ingress, treat that ingress as the current owner and plan a cutover/forwarding strategy.

For this user, we found:
- The Telegram bot already had a webhook at `https://copilot.bw-space.com/api/telegram/webhook`
- Telegram reported recent `502 Bad Gateway`
- Therefore the safe move was: prepare ai-department-os for Telegram, but defer actual cutover until URL/routing strategy is chosen

## Infra guidance
- Keep secrets in `.env.local`
- Keep `.env.example` scrubbed but structurally complete
- Validate with:
  - `npm run typecheck`
  - `npm run build`
- Prefer JSON repositories first; only move to Prisma/Supabase runtime persistence after entity/API contracts stabilize

## Verified intake persistence pattern
When bootstrapping or testing `/intake` in `/Users/brian/dev/ai-department-os`, use the repository's real JSON/store conventions instead of inventing an ad-hoc folder layout.

Observed implementation details:
- `POST /api/intake` reads `body.message` or `body.brief` as the freeform intake text
- title fallback is first 60 chars of the freeform message
- defaults in the current route:
  - `requestedBy: 'telegram-or-operator'`
  - `platform: 'Unspecified'`
  - `riskLevel: 'medium'`
  - `currentOwner: 'Brian'`
- `createProject()` writes canonical JSON files under:
  - `data/projects/<projectId>/project.json`
  - `tasks.json`
  - `handoffs.json`
  - `approvals.json`
  - `artifacts.json`
  - `events.json`
- project ids currently follow `vid-YYYYMMDD-xxxxxx`
- the project record starts with status `intake`
- when a brief is provided, the repo creates a `brief` artifact immediately and appends `project_created` plus `artifact_written` events

Useful manual-seed pattern for operator demos or Telegram flow testing:
- Create the project JSON in `data/projects/<projectId>/project.json`
- Create empty collection files for tasks/handoffs/approvals
- Write a `brief` artifact entry to `artifacts.json`
- Mirror the markdown artifact content to `storage/projects/<projectId>/brief-v1.md`
- Append matching events in `events.json`

This gives a real, browseable project in `/projects` and `/projects/[id]` without needing mock-only changes, and is the safest way to stage visible phase reviews before deeper orchestration is wired.

## AI Director / intake follow-up pattern
When extending ai-department-os toward an AI Director system, do not stop at creating only the `brief` artifact from `/api/intake`.

Observed good v1 pattern:
1. `POST /api/intake` creates the project and `brief` artifact first
2. immediately generate a draft Director direction artifact
3. immediately generate a draft execution-graph artifact
4. immediately create a pending Gate A approval row (`direction_lock`)

Recommended initial Gate A payload:
- `gate: 'direction_lock'`
- `requestedBy: 'director'`
- `artifactRefs`: include exact versions of the brief + direction draft + execution graph draft
- `riskNotes`: include any still-unknown audience / duration / forbidden-claims risks
- `approvalPayload`:
  - `gateLabel: 'Gate A — Brief / Direction Lock'`
  - `decisionScope`: explain what approving this allows downstream
  - `mustReview`: objective / audience / platform / tone / narrative direction / major constraints
  - `blockingQuestions`: 2-4 concrete missing decisions
  - `approvalSummary`: short operator-facing human-language summary
  - `rejectionRoute: 'director-direction'`

This pattern creates a real operator loop immediately:
intake → brief → direction draft → execution graph draft → approval queue.

## AI Director contract alignment finding
When adding AI Director concepts, there is currently no dedicated runtime artifact type for `execution-graph` or `director-direction` in `lib/domain/enums.ts`.

Safe v1 move:
- store direction and execution-graph drafts as `research` artifacts for now
- document the intended semantic meaning in `docs/contracts/`
- only add new runtime artifact enums after UI/API/repository expectations are aligned

This avoids breaking the existing repository validators while still letting `/projects/[id]` and `/approvals` show real data.

## Approval model alignment finding
If you enrich approval contracts with AI Director gate payloads, remember the runtime TypeScript layer must be updated too.

Minimum alignment steps:
- add an `ApprovalPayload` type in `lib/domain/types.ts`
- add `approvalPayload?: ApprovalPayload` to `ApprovalRecord`
- keep `riskNotes` available at runtime, not just in docs/contracts
- then patch `/api/intake` or approval routes to actually populate those fields

If you only update docs/contracts and forget runtime types, the schema looks advanced on paper but the app cannot safely produce or render the new review model.

## Mobile operator UX finding
For this user, a technically correct page is NOT enough. If the mobile preview mostly shows long text blocks, raw IDs, internal workflow concepts, or admin-console forms, the user experiences it as "一堆文字，沒有功效" even when the data model is working.

Therefore, when moving from backend skeleton to visible product value:
- do not keep expanding contracts first
- first create a mobile-readable decision layer
- optimize for "看得懂現在在做什麼 / 卡在哪 / 下一步要不要批" before adding more entities
- do NOT leave create-task / create-artifact / create-handoff / raw approval forms on the main operator-facing pages unless the user explicitly asked for operator tooling

Recommended v1 operator surfaces:
- project page top summary cards:
  - `目前方向`
  - `目前卡點`
  - `下一個決策`
- approval page decision cards:
  - `你正在決定什麼`
  - `批准後會發生什麼`
  - `若不批准會退回哪裡`
- project page control board:
  - `目前執行 Phase`
  - `可直接執行`
  - `待你拍板`
  - `最近產出`
  - `工作進度`

Implementation heuristic:
- put these summary cards ABOVE the long-form brief / graph / logs
- treat long documents as supporting detail, not the first thing the user sees
- if you must choose between a richer data model and a clearer mobile decision card, choose the decision card first
- if the user is interacting via Telegram, do not report localhost URLs as the handoff; produce a phone-usable tunnel URL and include the localtunnel safety IP if needed
- if the user says the site feels cluttered, aggressively remove admin surfaces and keep only decision board, progress, blockers, and next executable step

## Language / labeling finding
For this user, any in-progress front-end should default to Traditional Chinese, not English.

Minimum rule:
- top nav, page headings, metrics, button labels, form labels, approval controls, and status badges should be Traditional Chinese
- hide raw internal enums where possible
- translate status/gate labels with display helpers instead of leaking raw values like `direction_lock` or `approval_pending`
- old artifact/event content may still contain English, but the shell UI must not

## Phase 3 workflow-state finding
When moving from phase 2 data shape to a real SOP engine, the missing piece is not more entities — it is automatic state propagation between approvals, handoffs, artifacts, and the project record.

Minimum viable phase 3 rules that proved useful:
- creating a pending approval should automatically move the project to `approval_pending`
- `change_review` pending should also set `changeReviewRequired = true`
- approving `direction_lock` or `brief_lock` should set `scopeLockActive = true`, clear `changeReviewRequired`, move the project to `in_progress`, complete `intake-normalizer`, and advance `handoff-prep`
- approval `changes_requested` or `rejected` should move the project to `revise` (or `blocked` for terminal publish closeout), route ownership back via `rejectionRoute` fallback, and mark approval-prep as `needs_revision`
- sending a handoff should move the project to `review` and put the source task into `review`
- accepting a handoff should transfer `currentOwner` to `toRole` and complete the source task
- rejecting a handoff should return ownership to `fromRole`, set the project to `revise`, and mark the source task `needs_revision`
- after scope lock, creating a final substantive artifact (`brief`, `research`, `script`, `storyboard`, `edit-plan`, `prompt-pack`, `asset-checklist`) should auto-open a `change_review` approval
- after scope lock, creating a final `publish-pack` should auto-open `final_qa`

Implementation heuristic:
- keep the pure decision rules in `lib/server/sop-engine.ts`
- keep persistence + side effects in `lib/server/repositories.ts`
- use small repository helpers such as `patchTask(...)` and `syncProjectAfter...(...)` rather than burying logic in routes

## Pitfalls
- Don’t wire UI directly to mock data after repository layer exists
- Don’t persist derived fields as canonical truth unless necessary
- Don’t jump to Prisma too early; it hardens unstable shapes
- Don’t assume polling works for Telegram without checking webhook ownership
- Don’t expose internal enum/state names directly in operator UI
- Don’t introduce new semantic artifact concepts in docs only; either map them to existing runtime artifact types or update runtime enums/types in the same pass
- Don’t create approval rows with only a status/gate name; include operator-readable decision payload so Telegram/UI can render human review cleanly
- Don’t mistake long-form brief/graph text for visible user value; surface decision summaries first
- Don’t ship English-first operator UI for this user; Traditional Chinese is the default delivery language
- Don’t leave approval/handoff/artifact writes as isolated CRUD; if state does not propagate to project/task ownership, the system still behaves like a database, not an operating system
- Don’t use line-numbered `read_file` output as the source for full-file rewrites. `read_file` prefixes lines like `12|...`; if you feed that text back into `write_file`/programmatic rewrites, you can silently corrupt `.ts` / `.tsx` files with embedded line numbers. For full-file rewrites, either:
  - use `write_file` with clean content you generated yourself, or
  - read raw file contents via terminal/Python stdlib before rewriting,
  then immediately run `npm run typecheck` and `npm run build` to catch corruption fast.

## Orchestration API finding
If `/api/orchestration/projects/[id]/plan` or `/api/orchestration/tasks/[id]/run` still return placeholder JSON, the system is not yet an operating system — it is only a data viewer.

Minimum useful move:
- add a server orchestration module (for example `lib/server/orchestration.ts`)
- `GET /api/orchestration/projects/[id]/plan` should derive missing stage tasks, runnable tasks, and blockers from the project workspace
- `POST /api/orchestration/projects/[id]/plan` should materialize the missing downstream tasks after scope lock
- `GET /api/orchestration/tasks/[id]/run` should preview whether a task is runnable and what artifact type it should produce
- `POST /api/orchestration/tasks/[id]/run` should actually create an artifact and let existing SOP propagation open the next approval when relevant

Implementation heuristic:
- keep plan derivation pure and repo-backed
- use repository helpers like `findTaskById(...)` and `updateTask(...)` instead of ad-hoc file writes in routes
- treat the first version as a skeleton executor that emits structured placeholder artifacts, then later swap in real subagent execution
- after each task execution, immediately update the task to reflect its produced artifact (`outputArtifactId`, review/completed state), resync downstream `inputArtifactIds`, and recompute next runnable tasks
- do not reopen completed / archived / canceled projects when materializing downstream tasks
- be careful with readiness rules: e.g. `edit-plan-track` should require both script and storyboard, not just one downstream artifact

Why this matters:
- it turns the product from static tracking into a controllable workflow engine
- it provides a safe intermediate step before wiring real autonomous agents
- it exposes the true next missing phase: dependency-aware auto-continue and agent-backed execution

## Project detail control-plane finding
Once orchestration exists, `/projects/[id]` should stop being only a detail page and become a phase control plane.

Minimum useful operator layer:
- load the orchestration plan on the page server-side
- show `current execution phase`, `runnable task count`, `missing task count`, and `orchestration blocker`
- provide a server action to materialize missing downstream tasks
- provide a server action per runnable task to execute it directly from the page
- render the pipeline grouped by phase, with per-task status, owner, readiness, and direct action buttons

UX rule for this user:
- keep the control block ABOVE long-form artifacts/events
- translate pipeline task names and owner roles into Traditional Chinese before showing them in the control panel and task list
- if browser verification still shows raw labels like `research-track`, `visual-reference-track`, `storyboard-track`, or roles like `visual-design`, patch the shared display mapping immediately

## Phase B dependency propagation finding
After the first orchestration API pass, a major gap remains if tasks are only materialized but not kept in sync.

Observed failure mode:
- downstream tasks get created with empty or stale `inputArtifactIds`
- running an upstream task does not update later tasks
- the system can list many queued tasks, but the real next runnable set is inaccurate
- a "completed" project can be accidentally re-expanded if there is no status guard

Minimum useful follow-up:
- when materializing downstream pipeline tasks, seed `inputArtifactIds` from the latest relevant artifacts
- after every task execution, update that task to `review`, persist `outputArtifactId`, and refresh downstream `inputArtifactIds`
- recalculate `nextRunnableTasks` from artifact availability instead of assuming stage order alone
- add a guard so `completed`, `archived`, and `canceled` projects do not materialize new downstream tasks
- tighten readiness checks where multiple prerequisites are actually required (for example `edit-plan-track` should require both `script` and `storyboard`, not only one of them)

Implementation heuristic:
- keep input resolution in a pure helper such as `resolveTaskInputArtifactIds(...)`
- add a sync pass like `syncPipelineTaskInputs(projectId)` after task execution and after plan materialization
- verify with a fresh project, not only legacy fixtures, because old seeded data can hide missing dependency propagation

What good looks like:
- run `research-track` → `script-track` and `visual-reference-track` automatically update their inputs
- run `script-track` → `storyboard-track`, `edit-plan-track`, and `script-selection-join` receive updated inputs
- run `visual-reference-track` → `script-selection-join` becomes truly runnable once all required artifacts exist
- API responses include `nextRunnableTasks` so the controller can keep pushing instead of stopping at one task

## Phase 4 ingress + closeout finding
Two useful follow-up moves after phase 3:

## Phase 6.9 ingestion bridge finding
If wiki-derived memory / skill candidates are only visible in a queue, the system still feels incomplete. The missing piece is a real review lane that produces a decision result and opens the next apply lane.

Minimum useful implementation:
- keep the homepage queue, but do not stop at `已送進 review lane`
- each `ingestion-memory-review` / `ingestion-skill-review` task should support three explicit outcomes:
  - approved
  - changes_requested
  - rejected
- deciding the task should create a final review-result artifact (safe v1 choice: store it as `research`)
- the review-result artifact should include:
  - human-readable conclusion line first
  - decision
  - reviewer
  - source path
  - short summary
  - full source candidate snapshot
- if approved, automatically create the next apply task:
  - `hermes-memory-apply`
  - `hermes-skill-apply`
- store the result artifact path or source reference in the downstream apply task `blockingReason` so the operator can see what will be applied next

Visible UI rule:
- `/projects` should upgrade queue labels from merely `已送進 review lane` to status-rich outcomes like:
  - `已批准並產出結果`
  - `已要求補強`
  - `已拒絕送入`
- `/projects/[id]` should render ingestion review tasks inside `工作進度` with direct action buttons:
  - `批准送進 Hermes`
  - `要求補強`
  - `拒絕送入`
- after approval, the same page should visibly show:
  - review task completed
  - review result summary
  - newly created `Hermes memory 套用` / `Hermes skill 套用` queued tasks

Implementation heuristic:
- add a dedicated repository function such as `decideWikiIngestionTask(projectId, taskId, input)`
- this function should:
  1. validate the task is an ingestion review task
  2. read the source markdown from the stored wiki path
  3. create a final result artifact
  4. update the review task status (`done` / `needs_revision` / `canceled`)
  5. spawn the downstream apply task on approval
  6. append a project event that links review decision, result artifact, and apply task
- keep the result artifact human-readable; if the first visible line is only `decision: approved`, the UX still feels too internal

Why this matters:
- it turns ingestion from a passive queue into a real decision pipeline
- it gives the user a visible sense that the bridge is actually moving work forward
- it makes the remaining unfinished gap obvious: wiring the apply lane to real Hermes memory / skill ingestion

1. Extract intake orchestration into a shared server function (for example `lib/server/intake-flow.ts`) instead of keeping it only inside `/api/intake`
   - then both the HTTP route and Telegram `/intake` can call the same SOP entrypoint
   - this prevents Telegram from silently drifting into a weaker side-path that only creates projects

2. Treat publish as a mini workflow, not a single artifact write
   - final `publish-pack` after scope lock should open `final_qa`
   - approving `final_qa` should open a final `publish_closeout` approval
   - approving `publish_closeout` should complete the project and automatically create a final `retro` artifact

This creates the first real closeout loop:
publish artifact → final QA → closeout gate → retro artifact → completed project.

### Phase 6.9 apply-lane finding
When promoting wiki memory/skill candidates into real Hermes ingestion, do NOT treat a single project's closeout notes as automatically durable.

Observed reusable rule from repeated candidates:
- the stable reusable endgame is `final_qa -> publish_closeout`
- the earlier scope-lock gate (`brief_lock` vs `direction_lock`) varies by project and should remain project-specific unless repeated broadly

Promotion rule:
- promote repeated endgame patterns into durable memory or existing skills
- prefer patching an existing project skill when the candidate is a refinement of an already-loaded workflow
- for operator visibility, mark apply-lane tasks done only after the external Hermes ingest actually happened, and write a result artifact that names what was ingested (memory entry or skill patch)

## Interrupt-handling finding
When localhost.run tunnel notifications keep arriving, they can distract the controller into reactive webhook maintenance and stall the actual product roadmap.

Required controller discipline:
- treat tunnel/webhook rotation as a maintenance interrupt, not the new primary goal
- after each webhook update, immediately resume the previously active roadmap item from todo state
- keep a live todo item for the strategic workstream so maintenance messages do not reset execution focus
- before declaring a phase done, either start the next phase or run verification / regression checks yourself first

## Verification checklist
- `npm run typecheck` passes
- `npm run build` passes
- `/projects` can create a real project
- `/projects/[id]` can create task / artifact / handoff / approval
- `/approvals` can decide approval
- JSON files are written under `data/projects/<projectId>/`
- Telegram token can be validated with `npm run telegram:check`
- Telegram `/intake` uses the same intake orchestration as `/api/intake`
- final `publish-pack` can trigger `final_qa`
- approving `final_qa` can trigger `publish_closeout`
- approving `publish_closeout` can create a final `retro` artifact and complete the project
- closeout capture writes wiki closeout + memory-candidate + skill-candidate files
- `/projects` can function as a CEO exception board with separate sections for decisions, blocked/risk, closeouts, and active work
- If polling is attempted, confirm no active webhook conflict first
