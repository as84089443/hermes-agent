# Handoff Contract

Required fields:
- `id`
- `project_id`
- `from_task_id`
- `from_role`
- `to_role`
- `status`
- `summary`
- `artifact_ids`
- `assumptions`
- `open_questions`
- `risk_notes`
- `requested_review_type`
- `accepted_by`
- `accepted_at`
- `created_at`

Rules:
- every handoff must state explicit next owner
- no silent ownership transfer
- no handoff counts as complete until accepted
