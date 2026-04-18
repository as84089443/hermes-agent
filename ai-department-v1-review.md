# AI Department v1 review

## Minimum UI surfaces

1. Command Center (`/projects`)
   - Single list for all active projects
   - Columns/cards: title, status, current stage, next owner, deadline, last event, approval needed
   - Primary actions: new brief, open project, filter by waiting-on-human / active / blocked

2. Project Workspace (`/projects/[id]`)
   - One page with tabs/sections, not many standalone screens
   - Required sections: brief, artifacts, tasks/handoffs, approvals, activity log
   - v1 target = project can go from intake to publish pack on this page

3. Intake surface (`/new` modal or drawer, not a full product area)
   - Minimal brief form or pasted brief normalization
   - Create project + seed first tasks
   - Telegram/chat ingress can map into same schema; no separate heavy UI needed

4. Approval Queue (`/approvals`)
   - Human-only gate list
   - Show requested gate, artifact summary, risk notes, approve/revise buttons

Not needed in v1:
- dedicated `/agents`
- dedicated `/assets` as primary nav
- dedicated `/analytics`
- separate office/studio/research/writer shells
- multi-department boards
- render console

## Donor vs discard decisions

### Keep as donor
- `openclaw-office`
  - Keep only: ingress patterns, workflow/event stream concepts, approval-ish office surface, Telegram/public copilot routing patterns
  - Donor reason: already proves front door + workflow visibility + boss decision UI
  - Do not inherit its many product entrances (`/merchant`, `/ops`, `/writer`, `/browser`, `/research`)

- `BW_ContentStudio`
  - Keep only: project workspace patterns, proof-to-video domain model, campaign creation flow, campaign detail tabs, approve-before-render contract
  - Donor reason: strongest evidence for project work package UX and artifact shape
  - Trim billing/admin/marketing/auth sprawl from v1

- `producer-os-v2`
  - Keep only as schema donor for missions/handoffs/learning/status primitives
  - Donor reason: useful data model ideas, not a mature product shell
  - Do not use as frontend base for v1

- `reelforge`
  - Keep only as future async job/queue reference
  - Donor reason: BullMQ/worker separation is relevant later
  - Do not bring into v1 runtime unless render becomes mandatory

### Discard / do not carry forward into v1 shell
- `openclaw-office` multi-surface homepage and non-video business modules
- `BW_ContentStudio` pricing, billing, self-serve SaaS growth surfaces, broad admin area
- `producer-os-v2` current UI shell as-is
- `reelforge` current UI as-is
- legacy/parallel shells like `Star-Office-UI` or extra mission-control variants unless a single component is clearly reusable

## Migration policy

1. Migrate contracts first, code second
   - Freeze canonical schemas for `project`, `task`, `handoff`, `approval`, `artifact`, `event`
   - Freeze one artifact folder layout before copying UI logic

2. Use donor repos by slice, not by repo wholesale
   - UI slice from `openclaw-office`: intake/status/approval patterns
   - workspace slice from `BW_ContentStudio`: campaign/project detail composition
   - model slice from `producer-os-v2`: handoff + learning structures
   - infra slice from `reelforge`: only when async workers are actually needed

3. Prefer rewrite-over-port for UI shells
   - Copy patterns, naming, component ideas
   - Avoid dragging old route trees, auth assumptions, and env baggage

4. Port domain logic only when tied to proven workflow value
   - Example: proof-to-video campaign schema and approve-before-render
   - Avoid migrating billing, org admin, multi-tenant upgrades, queue plumbing in v1

5. Require donor acceptance criteria before importing any module
   - Does it map to canonical schema?
   - Can it run without legacy env/auth coupling?
   - Is it needed for v1 closed loop?
   - If no, document and leave behind

6. Migration order
   - Step 1: schema + state machine + artifact contract
   - Step 2: command center page
   - Step 3: project workspace page
   - Step 4: intake flow
   - Step 5: approvals queue
   - Step 6: 4 core workers + memory capture
   - Step 7: only then consider queue/render integration

7. Default policy for old repos
   - Read-only donors during v1 build
   - No attempt to preserve cross-repo runtime compatibility unless required by ingress
   - New product becomes canonical; old repos become references and fallback utilities

## Concrete patches

1. Blueprint: replace the v1 route list with a stricter minimum
   - From: `/projects`, `/projects/[id]`, `/approvals`, `/agents`, `/assets`, `/analytics`, `/settings/brand`, `/settings/workflows`
   - To: `/projects`, `/projects/[id]`, `/approvals`, `/settings`
   - Rationale: `/agents`, `/assets`, `/analytics` should be embedded sections until phase 2

2. Blueprint: add explicit “one-page workspace” rule
   - `project detail` must contain brief, artifact tabs, task/handoff timeline, approvals, activity log on one route
   - Avoid splitting v1 into office page + studio page + asset page

3. Blueprint: add donor policy table
   - `openclaw-office = ingress + approval donor`
   - `BW_ContentStudio = workspace/domain donor`
   - `producer-os-v2 = model donor only`
   - `reelforge = future infra donor only`

4. Blueprint: add a “no wholesale adoption” rule
   - No repo gets carried over as the product shell intact
   - Every imported module must map to canonical schema and v1 closed loop

5. Blueprint: narrow v1 worker/output scope
   - v1 publish pack = brief, research memo, script, storyboard, asset checklist, QA report, publish pack
   - Mark prompt pack/edit plan/analytics-learning as optional or phase 1.5 to keep first pilot lighter

6. Control Center: add a new top route for “AI Department v1 build rules”
   - Summarize one-product rebuild, minimal UI, donor policy, migration order
   - Make it the shortest operator reference

7. Control Center: classify pages by decision level
   - `ecosystem-map = donor landscape`
   - `rebuild-blueprint = target architecture`
   - `control-center = operator front door`
   - Add note that v1 UI should collapse to command center + project workspace + approvals

8. Ecosystem map: revise phase-1 front door wording
   - Instead of `openclaw-office` as the front door of the product, say it is the strongest donor for intake/status/approval patterns
   - This aligns with one-product rebuild and avoids locking v1 to legacy shell

9. Blueprint: add “read-only donor window” policy
   - During v1, old repos are mined and referenced but not treated as co-evolving source-of-truth products
   - Reduces coupling and migration drag

10. Blueprint: add a kill-switch rule for render/queue
   - If first pilot can end at publish pack without auto-render, keep render external/manual
   - Do not import BullMQ/worker stack before repeated human-approved demand proves it necessary
