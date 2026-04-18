# Artifact Contract

Required fields:
- `id`
- `project_id`
- `type`
- `version`
- `status`
- `path`
- `produced_by_task_id`
- `checksum`
- `created_at`

Rules:
- v1 canonical artifact set: brief, research memo, script, storyboard, qa report, publish pack, retro
- optional phase 1.5: prompt pack, edit plan, asset checklist
- once reviewed or approved, a new version must be created instead of overwriting
