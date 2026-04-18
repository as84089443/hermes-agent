# AI Department OS v1 Minimal Data Model and Contracts

Date: 2026-04-13

Purpose:
Define the smallest practical canonical data model and machine-readable contracts for ai-department-os v1.

Source basis:
- `/Users/brian/wiki/concepts/hermes-ai-department-rebuild-blueprint.md`
- `/Users/brian/wiki/concepts/bw-sop-decision-rails.md`
- `/Users/brian/dev/hermes-agent/docs/specs/subagent-parallel-execution-fabric.md`

Design stance:
- v1 only covers the closed loop needed to move one project from intake to publish pack.
- Keep project state separate from task / handoff / approval / artifact details.
- Every review and approval must point to exact artifact version(s).
- Every transition must be traceable through Event rows.
- Avoid duplicating brief content in the Project row.

Recommended contract filenames:
- `docs/contracts/ai-department-os/v1/project.contract.json`
- `docs/contracts/ai-department-os/v1/task.contract.json`
- `docs/contracts/ai-department-os/v1/handoff.contract.json`
- `docs/contracts/ai-department-os/v1/approval.contract.json`
- `docs/contracts/ai-department-os/v1/artifact.contract.json`
- `docs/contracts/ai-department-os/v1/event.contract.json`

Recommended status enums:
- Project: `intake | triage | in_progress | review | revise | approval_pending | publish_pack_ready | completed | archived | blocked | canceled`
- Task: `queued | in_progress | review | needs_revision | done | blocked | canceled`
- Handoff: `drafted | sent | accepted | rejected`
- Approval: `pending | approved | changes_requested | rejected`
- Artifact: `draft | final | superseded`

## 1) Project

Minimum purpose:
The project row is the control-plane anchor for routing, ownership, deadline, and folder location.

Persisted fields:
- `id`
- `title`
- `status`
- `current_owner`
- `requested_by`
- `platform`
- `deadline`
- `risk_level`
- `folder_path`
- `recurrence_key`
- `created_at`
- `updated_at`

Derived fields:
- `scope_lock_active`
  - derived from current stage / approval state / selected gate rules
- `change_review_required`
  - derived when a post-lock change touches protected scope fields or approved artifacts
- `next_gate`
  - derived from status + open tasks + open approvals
- `waiting_on_human`
  - derived from approval state / escalation state

Notes:
- Brief content such as objective, audience, tone, CTA, constraints should live in the `brief` artifact, not duplicated on Project.
- `current_owner` is mandatory. No ownerless project.
- `recurrence_key` is optional but should exist in v1 as the minimum recurring concept.

## 2) Task

Minimum purpose:
Represents one worker or orchestrator unit of execution tied to artifacts.

Persisted fields:
- `id`
- `project_id`
- `type`
- `status`
- `owner_role`
- `input_artifact_ids`
- `output_artifact_id`
- `due_at`
- `blocking_reason`
- `created_at`
- `completed_at`

Derived fields:
- `ready_for_execution`
  - derived from prerequisite artifacts / prior task completion / execution graph freeze
- `overdue`
  - derived from `due_at` and terminal status
- `review_required`
  - derived from task type or gate placement

Notes:
- Keep next ownership out of Task. That belongs in Handoff.
- `output_artifact_id` may be null until completion.

## 3) Handoff

Minimum purpose:
Captures structured transfer between roles with explicit acceptance state.

Persisted fields:
- `id`
- `project_id`
- `from_task_id`
- `from_role`
- `to_role`
- `status`
- `summary`
- `artifact_ids`
- `assumptions`
- `findings`
- `open_questions`
- `risk_notes`
- `requested_review_type`
- `next_action`
- `accepted_by`
- `accepted_at`
- `created_at`

Derived fields:
- `is_waiting_acceptance`
  - derived from `status=sent`
- `has_open_blockers`
  - derived from `open_questions` and risk severity rules

Notes:
- `accepted_by` and `accepted_at` must exist as fields in v1 even if null before acceptance.
- No handoff without acceptance state.
- This contract follows the parallel execution fabric requirement that every handoff include findings, assumptions, open questions, risks, and explicit next action.

## 4) Approval

Minimum purpose:
Represents formal gate or human review decisions against exact artifact versions.

Persisted fields:
- `id`
- `project_id`
- `gate`
- `status`
- `requested_by`
- `requested_at`
- `reviewed_by`
- `reviewed_at`
- `artifact_refs`
- `decision_notes`

Derived fields:
- `waiting_on_human`
  - derived from `status=pending` and gate policy
- `blocks_project`
  - derived from gate type and unresolved pending state

Notes:
- Use `artifact_refs` instead of bare artifact IDs so approval always binds to exact version.
- Minimum `artifact_refs` item: `{ artifact_id, version }`.
- No approval without exact artifact version.

## 5) Artifact

Minimum purpose:
Represents a canonical produced output or snapshot under review.

Persisted fields:
- `id`
- `project_id`
- `type`
- `version`
- `status`
- `path`
- `produced_by_task_id`
- `supersedes_artifact_id`
- `checksum`
- `created_at`

Derived fields:
- `immutable_ref`
  - derived from id + version
- `is_latest_version`
  - derived by comparing versions within the same project and artifact type

Notes:
- v1 should mark replaced outputs as `superseded`, not overwrite them.
- `supersedes_artifact_id` is the minimum lineage field needed for branch merge and version replacement.

## 6) Event

Minimum purpose:
Append-only audit row for all important transitions and actions.

Persisted fields:
- `id`
- `project_id`
- `entity_type`
- `entity_id`
- `event_type`
- `actor`
- `payload_json`
- `created_at`

Derived fields:
- none required in v1

Notes:
- Keep Event append-only.
- Minimum event types for v1:
  - `project_state_changed`
  - `task_created`
  - `task_state_changed`
  - `handoff_sent`
  - `handoff_accepted`
  - `approval_requested`
  - `approval_decided`
  - `artifact_written`
  - `branch_merged`
  - `escalation_raised`

## Minimal relationship model

- One Project has many Tasks.
- One Project has many Handoffs.
- One Project has many Approvals.
- One Project has many Artifacts.
- One Project has many Events.
- One Task may produce zero or one canonical output Artifact.
- One Handoff references one or more Artifacts.
- One Approval references one or more exact Artifact versions.
- One Artifact belongs to exactly one Project and is produced by one Task.
- Every state transition should emit an Event.

## What is intentionally out of scope for v1

To keep v1 implementable, do not create separate top-level entities yet for:
- client / organization / account
- execution graph nodes and edges as first-class tables
- billing / CRM
- rich asset library indexing
- publish receipts beyond artifact + event records
- analytics dimensions beyond artifact + event + retro capture

If needed, execution graph metadata can live in Task `type`, Handoff, and Event `payload_json` until v2.

## Contract file conventions

All six JSON contracts use these rules:
- `x-storage: persisted` means store as canonical source of truth.
- `x-storage: derived` means compute on read or through application logic; do not store as the primary canonical field in v1.
- Fields that are required but may not yet have a value should be present with `null`.
- Timestamps use ISO 8601 strings.
- Arrays default to empty arrays, not null, where practical.

## Suggested implementation order

1. Freeze these six contracts.
2. Implement enum validation and relationship checks.
3. Make approvals bind to exact artifact versions.
4. Make every transition emit Event rows.
5. Only after that, build UI surfaces and worker adapters.
