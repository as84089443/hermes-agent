# Task Contract

Required fields:
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

Rules:
- one task should produce one primary artifact type
- downstream ownership is expressed through handoff, not duplicated on task
- all task state changes emit events
