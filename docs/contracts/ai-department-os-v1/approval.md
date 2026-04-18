# Approval Contract

Required fields:
- `id`
- `project_id`
- `gate`
- `status`
- `requested_by`
- `requested_at`
- `reviewed_by`
- `reviewed_at`
- `artifact_ids`
- `decision_notes`

Rules:
- approval must point to exact artifact version under review
- final publish approval always requires human review
- all approval decisions emit events
