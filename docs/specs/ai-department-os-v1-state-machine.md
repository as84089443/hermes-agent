# AI Department OS v1 State Machine

## Project states

Primary:
- `intake`
- `triage`
- `in_progress`
- `review`
- `revise`
- `approval_pending`
- `publish_pack_ready`
- `completed`
- `archived`

Side states:
- `blocked`
- `canceled`

Rules:
- project must always have `current_owner`
- any transition must emit an event row
- scope lock can become active after script selection or QA gate

## Task states

- `queued`
- `in_progress`
- `review`
- `needs_revision`
- `done`
- `blocked`
- `canceled`

## Handoff states

- `drafted`
- `sent`
- `accepted`
- `rejected`

Rule:
- no handoff is complete without `accepted_by` and `accepted_at`

## Approval states

- `pending`
- `approved`
- `changes_requested`
- `rejected`

Rule:
- every approval must reference exact artifact ids and versions

## Artifact states

- `draft`
- `final`
- `superseded`

Rule:
- artifacts under review are never overwritten in place
- superseded branches remain traceable

## Scope lock and change review

Scope lock becomes active when:
- script is selected for downstream work
- QA gate begins
- publish pack enters approval

Formal change review required if a locked project changes:
- target platform
- core message or CTA
- duration
- deliverable scope
- risk level needing human approval
- already approved artifact

## UI label mapping

Do not expose raw enums to operators.

Preferred UI labels:
- `review` -> Waiting on Review
- `approval_pending` -> Ready for Approval
- `revise` -> Needs Rework
- `blocked` -> Blocked
- human gate pending -> Waiting on Human
