# AI Department OS v1 Pages and Routes

## Product shell rule

v1 只有一個產品殼：`ai-department-os`。
不要拆 office / studio / research / writer 多前台。

## Required pages

### `/projects`
Operator job:
- 看 active / blocked / waiting-on-human
- 找出今天先處理的專案
- 建立新 project 或進入既有 project

Required widgets:
- project list
- filters
- waiting-on-human slice
- blocked slice
- quick create action

### `/projects/[id]`
Operator job:
- 檢視 canonical brief
- 檢視 artifact versions
- 發出或接受 handoff
- 送審 / 批准 / 退回
- 看完整 activity log

Required sections:
- brief
- artifacts
- tasks and handoffs
- approvals
- activity log

### `/approvals`
Operator job:
- 快速完成 human review
- 看到 gate、artifact version、risk、decision buttons

### `/settings`
Operator job:
- 維護品牌規則
- 維護 workflow rule
- 維護風險與審核門檻

## Required API routes

- `POST /api/intake`
- `GET|POST /api/projects`
- `GET|PATCH /api/projects/[id]`
- `GET|POST /api/projects/[id]/tasks`
- `GET|POST /api/projects/[id]/handoffs`
- `GET|POST /api/projects/[id]/approvals`
- `GET|POST /api/projects/[id]/artifacts`
- `GET /api/projects/[id]/events`
- `POST /api/approvals/[id]/decision`
- `POST /api/orchestration/projects/[id]/plan`
- `POST /api/orchestration/tasks/[id]/run`

## Explicitly out of v1 shell

Do not create these as first-class nav items in v1:
- `/agents`
- `/assets`
- `/analytics`
- `/render`
- `/publishing`

If needed, show them as sections inside `/projects/[id]`.
