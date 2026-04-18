# Hermes AI Department Subagent Parallel Execution Fabric Proposal

Date: 2026-04-13

Goal:
Define a subagent-first execution fabric for AI Department OS so multiple specialists can run in parallel under Hermes orchestration while preserving human gates, auditability, and wiki/memory capture.

## Parallel execution model

### 1) Core principle
- Orchestrator does not execute most domain work itself.
- Orchestrator decomposes work into typed tasks and launches parallel specialists through delegate_task.
- Specialists exchange structured handoffs through project state + artifact refs, not chat-only context.
- The fabric should support both orchestrator-routed fan-out and specialist-to-specialist mesh handoffs.
- cron is used for watchdogs, SLA checks, retries, review nudges, and retro scheduling.
- memory stores durable execution summaries, reusable constraints, and department heuristics.
- wiki stores canonical contracts, review policies, and validated lessons.

### 2) Execution fabric layers
1. Intake + planning
   - Normalize brief
   - Classify risk, deadline, scope, and required roles
   - Build execution graph
2. Parallel specialist mesh
   - Launch independent specialists for tasks with no blocking artifact dependency
   - Allow lateral handoffs between specialists when contract permits
3. Review + merge
   - Merge artifacts into a project-level decision bundle
   - Run QA / compliance review
4. Human gate
   - Require approval for strategy shifts, sensitive claims, legal risk, and final publish
5. Closure + learning
   - Write final artifacts
   - Capture retro into memory
   - Promote durable lessons into wiki

### 3) Canonical execution graph pattern
Use a DAG instead of a single fixed chain.

Example for video department v1:
- intake-normalizer -> orchestrator-plan
- orchestrator-plan -> parallel:
  - research
  - strategy
  - asset-planner
- research + strategy -> script
- script + asset-planner -> storyboard
- storyboard -> parallel:
  - edit-pack
  - qa-preflight
- edit-pack + qa-preflight -> qa-compliance
- qa-compliance -> human approval gate
- approved -> publish-packager
- publish-packager -> analytics-learning
- analytics-learning -> memory capture -> wiki promotion candidate

### 4) Hermes-specific runtime rules
- delegate_task is the default mechanism for specialist execution.
- Each delegated run must include:
  - project_id
  - task_id
  - role
  - objective
  - input_refs
  - required_output_types
  - deadline or SLA
  - escalation thresholds
- Every specialist must write:
  - primary artifact
  - handoff record
  - status event
  - memory candidate summary
- cron jobs must cover:
  - stuck task detection
  - overdue review reminders
  - unmerged parallel branch detection
  - post-approval follow-up
  - retro scheduling
- memory writes are allowed for project and department memory; wiki promotion requires validation or approval.

## Serial gates

### 1) Always serial
These steps require ordered progression because they define scope, authority, or release state.
- brief normalization before graph creation
- graph creation before parallel dispatch
- script after research baseline is available
- final QA/compliance after all candidate artifacts exist
- human approval before publish-ready status
- publish packaging before release scheduling
- retro closeout before archive

### 2) Parallel-safe roles
These roles can run concurrently once the brief and task graph exist.
- research
- strategy
- operations / asset-planner
- client/service clarification
- reference gathering
- packaging prep without release action
- analytics setup
- preflight QA on partial artifacts

### 3) Conditionally parallel roles
These can run in parallel only when artifact contracts are explicit.
- script variants can run in parallel against the same research memo
- storyboard exploration can run in parallel across approved script variants
- creative packaging can run in parallel with QA preflight, but not with final QA signoff
- knowledge extraction can begin before final publish, but wiki promotion waits until approval

### 4) Required join points
The orchestrator must force a merge at these points.
- after parallel discovery branches produce a unified planning packet
- before script selection if multiple research/strategy branches disagree
- before final QA if edit-pack, asset checklist, and claims evidence are incomplete
- before publish if any open risk remains

## Review rules

### 1) Handoff contract
Every handoff must include:
- from_role
- to_role
- artifact_refs
- summary
- assumptions
- findings
- open_questions
- risks with severity
- requested_review_type
- next_action
- escalation_if_not_resolved_by

No handoff may be considered complete without artifact refs and a named next owner.

### 2) Review classes
- Peer review:
  - specialist checks another specialist output for completeness or dependency fitness
  - allowed without human intervention
- Gate review:
  - QA/compliance or orchestrator verifies contract completion before status transition
- Human review:
  - required for brand strategy changes, rights/legal ambiguity, sensitive factual claims, and final publish
- Escalation review:
  - triggered when blockers exceed SLA, branches conflict materially, or QA fails repeatedly

### 3) Escalation triggers
Escalate to orchestrator immediately when:
- required artifact missing
- conflicting conclusions across parallel branches
- dependency blocked for longer than SLA
- high-risk claim or policy issue detected
- same task is revised more than 2 times

Escalate to human gate when:
- brand direction changes
- medical, legal, financial, or reputational risk appears
- copyright/licensing uncertainty exists
- publish action is requested

### 4) Auditability rules
- All task launches, status transitions, handoffs, approvals, and escalations must create event records.
- Orchestrator must preserve branch lineage for parallel runs.
- Final project bundle must show which branch won, which artifacts were superseded, and why.
- memory entries must link back to task_id, artifact path, and approval state.
- wiki promotion must reference validated source artifacts, not draft-only outputs.

## Concrete patches

### Patch A: /Users/brian/wiki/concepts/hermes-ai-department-agent-map.md
Add a new section after "Operating model":

- Introduce "Subagent-first execution fabric"
- State that orchestrator primarily delegates through parallel specialists instead of doing domain work itself
- Add a "Parallel-capable roles" list:
  - Research, Strategy, Asset Planner, Client Clarification, Preflight QA, Packaging Prep, Analytics Setup
- Add a "Serial gates" list:
  - Brief normalization
  - Execution graph freeze
  - Final QA / compliance
  - Human approval
  - Publish release
  - Retro closure
- Replace the single "Handoff order" line with:
  - a canonical default path
  - a note that actual execution is a DAG with parallel branches and join points
- Add rule:
  - specialists may hand off laterally if they use the structured handoff contract and emit an event

Suggested bullets to insert:
- Orchestrator 以 delegate_task 啟動多個專門子代理，不把所有推理集中在單一 agent。
- 預設流程是 DAG，不是只能線性 pipeline；只要沒有 artifact 依賴衝突，就應優先平行化。
- 每個平行 branch 都必須回寫 task event、artifact refs、handoff summary，才能進入 merge。
- human 只在策略、合規、版權、最終發佈 gate 介入。

### Patch B: /Users/brian/wiki/concepts/hermes-ai-department-rebuild-blueprint.md
Expand "Canonical target system" and "Five-layer architecture" with a dedicated execution fabric subsection:

- Add new object to core objects:
  - `execution_edge`
  - `review_request`
  - `escalation`
- Add a new subsection under control plane:
  - execution graph planner
  - branch merge controller
  - SLA watchdog via cron
- Update department worker plane rules:
  - workers may publish to more than one downstream candidate owner, but only one active next owner may advance the canonical branch
  - lateral peer review is allowed before orchestrator merge
- Add explicit mention that Hermes delegate_task + cron + memory + wiki are first-class infrastructure for the worker plane
- Extend project state plane with branch-aware substate or task-level status tracking so multiple tasks can be in_progress simultaneously under one project
- Add knowledge plane rule:
  - project memory captures branch outcomes; wiki only stores validated patterns after review

Suggested insertions:
- 平行執行層位於 control plane 與 worker plane 之間，負責把 project 拆成可並行的 task DAG。
- orchestrator 必須知道哪些 task 可 fan-out、哪些 task 必須 join、哪些 task 需要 human gate。
- cron 負責 branch watchdog、SLA 提醒、review 逾時升級與 retro 排程。
- memory 記錄專案級 branch 決策與可重用 heuristics；wiki 只收斂已驗證 SOP 與規則。

### Patch C: /Users/brian/dev/hermes-agent/docs/plans/2026-04-13-hermes-ai-department-rebuild-plan.md
Add a new task after Task 6:

## Task 6.5: Define the subagent parallel execution fabric

Objective:
Specify how Hermes launches, tracks, merges, reviews, and escalates concurrent specialist runs.

Files:
- Create: `docs/specs/subagent-parallel-execution-fabric.md`
- Modify: `docs/specs/hermes-orchestration-integration.md`
- Modify: `docs/specs/ai-department-state-machine.md`
- Modify: `docs/specs/ai-department-data-model.md`

Step 1: Define execution graph schema
Required fields:
- node_id
- role
- dependency_refs
- parallel_group
- join_rule
- sla_minutes
- escalation_target

Step 2: Define runtime actions
- delegate_task fan-out
- branch status sync
- join/merge decision
- cron watchdogs
- memory capture
- wiki promotion

Step 3: Define review and escalation rules
- peer review
- QA gate review
- human approval review
- repeated-failure escalation

Step 4: Verification
- can two or more specialists run on one project without losing auditability?
- can the winning branch and rejected branches both be explained later?
- can a blocked dependency be escalated automatically?

Also update Task 6 responsibilities from "create task sequence" to "create execution graph" and add explicit mention of parallel dispatch and branch merge.

### Patch D: /Users/brian/dev/hermes-agent/docs/plans/2026-04-13-multi-department-agent-operating-model.md
Strengthen "Parallel Specialist Mesh" from a high-level pattern into the default operating model for qualified tasks.

Add a new subsection after "模式 C：Parallel Specialist Mesh":

### 模式 D：Subagent-first Execution Fabric
- Orchestration 先把任務轉成 execution graph，而不是單純排成單線流程。
- 以 delegate_task 同時啟動多個專家 agent。
- 專家 agent 可在規則內彼此 lateral handoff，不必所有資訊都先回到 orchestrator 才能前進。
- orchestrator 保留 branch merge、狀態推進、衝突仲裁、human gate 管理權。
- cron 持續巡檢 stuck tasks、join timeout、review timeout、retro follow-up。
- memory / wiki 分別承接短中期經驗與長期制度化知識。

Add a new subsection under routing rules:
- parallel if no blocking artifact dependency, low coupling, and review contract is defined
- serial if authority transfer, release state, or compliance signoff is involved
- require join before any external-facing artifact becomes canonical

Add a new subsection under structured handoff spec:
Required fields:
- assumptions
- requested_review_type
- escalation_if_not_resolved_by
- branch_id
- parent_task_id

Add a new subsection under state machine:
- project state remains canonical at project level
- task states may progress concurrently under the same project
- add join_waiting and escalated as task-level states if needed

Add a new subsection under observability:
- branch merge latency
- branch conflict rate
- escalation frequency
- time-to-human-gate
- memory promotion rate

## Recommended implementation stance
- Keep the human gate narrow but explicit.
- Prefer mesh collaboration among specialists over orchestrator-only relay.
- Preserve one canonical branch for release, but retain full branch history for audit.
- Use wiki for stable operating knowledge and memory for execution residue.
