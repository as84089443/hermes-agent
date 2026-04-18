# Event Contract

Required fields:
- `id`
- `project_id`
- `entity_type`
- `entity_id`
- `event_type`
- `actor`
- `payload_json`
- `created_at`

Minimum event types:
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
