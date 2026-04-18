# Project Contract

Required fields:
- `id`
- `title`
- `status`
- `current_owner`
- `requested_by`
- `platform`
- `deadline`
- `risk_level`
- `folder_path`
- `scope_lock_active`
- `change_review_required`
- `created_at`
- `updated_at`

Notes:
- brief content lives in artifact `brief`, not duplicated on project row
- project can never exist without `current_owner`
- project status is delivery progress only; task/approval details stay in their own records
