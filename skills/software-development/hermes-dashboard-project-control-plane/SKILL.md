---
name: hermes-dashboard-project-control-plane
description: Extend Hermes Agent's built-in 9119 dashboard from a session/status viewer into a real project control plane with a persisted project ledger, non-blocking project push actions, an autopilot driver, and boss-mode project/approval pages.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, dashboard, project-control-plane, autopilot, fastapi, react, sqlite, boss-mode]
---

# Hermes Dashboard Project Control Plane

Use this when working in the `hermes-agent` repo and the goal is to turn the built-in dashboard at `http://127.0.0.1:9119/` into a real project/agent operations surface rather than a session-history viewer.

This is specifically for the built-in Hermes dashboard (`hermes_cli/web_server.py` + `web/src/*`), not ai-department-os.

## When to use
- The user wants to control agents and project progress from the Hermes web UI
- The current control center is too heuristic / wiki-driven / session-driven
- You need a lightweight project ledger inside Hermes itself
- The current "push forward" action blocks the UI while waiting for a full agent run
- You need an inspectable periodic autopilot loop with noop guardrails

## What worked

## 1. Add a separate lightweight project ledger instead of overloading SessionDB
Do not try to store project state in `hermes_state.py` transcripts or `todo` state.
Create a separate SQLite-backed runtime ledger module.

Worked file:
- `hermes_project_state.py`

Useful minimal entities:
- `projects`
- `tasks`
- `artifacts`
- `approvals`
- `events`

Important fields on `projects`:
- `main_phase`
- `phase_goal`
- `next_action_type`
- `next_action_summary`
- `autopilot_enabled`
- `waiting_reason`
- `last_cycle_at`
- `last_cycle_status`
- `last_cycle_summary`
- `session_id`

Important rule:
- keep this as a separate control plane that complements SessionDB instead of replacing it
- SessionDB remains the transcript/audit layer for conversations
- the project ledger becomes the source of truth for project progression

## 2. Expose project APIs directly from `hermes_cli/web_server.py`
Useful endpoints that proved enough for a first working control plane:
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/push`
- `POST /api/projects/{project_id}/pause`
- `POST /api/projects/{project_id}/resume`
- `POST /api/projects/{project_id}/approvals/request`
- `GET /api/approvals`
- `POST /api/approvals/{approval_id}/decide`
- `POST /api/projects/{project_id}/review`
- `POST /api/projects/{project_id}/verify`
- `POST /api/projects/{project_id}/escalate`
- `GET /api/autopilot/driver`
- `POST /api/autopilot/driver`

Good split:
- `push` = launch or queue real progression work
- `review` = write review verdict back to task/project ledger
- `verify` = write verification artifact + verification event
- `escalate` = mark project/task blocked with explicit reason

## 3. The "push" action must be non-blocking
Critical real-world finding:
- A synchronous `POST /api/projects/{id}/push` that waits for a full `AIAgent` run makes the web UI feel frozen.
- The user experiences this as "card stuck / whole site stuck" even when the backend is just busy.

Working fix:
- queue the project push in the background with `asyncio.create_task(...)`
- return immediately with `queued: true`
- update project state to `running` before returning
- let the page poll for updates

Useful pattern:
- keep `_PROJECT_PUSH_TASKS: Dict[str, asyncio.Task]`
- if the same project is already running, return the current project state instead of launching another run
- write an immediate status summary like:
  - `Hermes 正在背景推進這個專案…`

This is much better than blocking the HTTP request until a full agent loop finishes.

## 4. Add a real autopilot driver, not just cron-ish language in the UI
A useful first version can live inside `hermes_cli/web_server.py` if you are still in a bootstrap phase.

Worked pattern:
- keep global singleton state like:
  - `started`
  - `status`
  - `interval_seconds`
  - `last_cycle_at`
  - `last_cycle_reason`
  - `last_summary`
  - `last_error`
  - `task`
- expose it via `/api/autopilot/driver`
- start it lazily when `/api/control-center` or `/api/projects` is first hit
- have a loop that wakes every N seconds and scans the project ledger

Good first eligibility rules:
- skip terminal states: `completed`, `archived`, `cancelled`
- skip paused projects
- if `open_approvals > 0`, return noop
- if already running, skip
- otherwise queue a background project push

## 5. Add a noop guard for waiting-on-human so the dashboard does not fake progress
This was a crucial experiential finding.

Without a noop guard:
- the driver keeps revisiting projects that already have pending approvals
- the dashboard appears active, but it is just rewriting the same state
- event streams get noisy
- operator trust drops

Working result shape:
- `noop_already_waiting_on_human_approval`

Recommended behavior:
- manual driver trigger should report noop clearly
- interval driver should also report noop clearly
- do not rewrite identical waiting state just to look active

## 6. Make writeback real: push -> artifact/event/task updates
A project push should not only change summary text.
It should write durable control-plane state.

Useful pattern after a successful agent run:
1. write an `agent-output` artifact
2. mark the latest task `done`
3. attach `output_artifact_id`
4. preserve `child_session_id`
5. append event rows
6. then update `last_cycle_*` on the project

This keeps the dashboard from being just a pretty wrapper around chat summaries.

## 7. Add explicit review / verify / escalate writeback endpoints
These made the system much more trustworthy.

Working semantics:
- `review`
  - verdict like `PASS`
  - task status becomes `review_passed`
  - project state remains actionable
  - event: `review_decided`
- `verify`
  - creates a `verification-report` artifact
  - task status becomes `verified`
  - event: `artifact_written` + `verification_recorded`
- `escalate`
  - project status becomes `blocked`
  - task status becomes `blocked`
  - `waiting_reason` / `blocking_reason` are set
  - event: `escalation_raised`

These are much better than leaving review/verify/escalation as plain chat text.

## 8. Extend the React shell with real pages, not just more cards on the old control center
Useful additions to `web/src/App.tsx`:
- `專案`
- `審批`

Worked pages:
- `web/src/pages/ProjectsPage.tsx`
- `web/src/pages/ApprovalsPage.tsx`

What `/projects` should do in v1:
- create a new project
- list projects with status / main phase / next step / open approvals / open tasks
- provide buttons for:
  - push
  - pause
  - resume
  - view detail
  - open related agent session
- show a project detail pane on the same page for fast operator review

What `/approvals` should do in v1:
- show a real pending approval queue
- explain:
  - what you are deciding
  - what happens if approved
  - what happens if rejected
- provide direct actions:
  - approve
  - changes requested
  - reject

## 9. Keep boss-mode language in Traditional Chinese and hide internal jargon by default
This matters a lot for this user.

Good patterns:
- prefer `目前方向 / 目前卡點 / 下一個決策`
- prefer `待你拍板` over internal gate names
- expose raw ids/types only in secondary detail if necessary
- keep the top of the page human-readable first

## 10. Use a shared boss-mode translation layer instead of ad-hoc per-page wording
A reusable frontend pattern emerged during the boss-mode rewrite.

Create and extend a single helper layer such as:
- `web/src/lib/boss_mode_labels.ts`

Put the humanization logic there instead of scattering it across page components.

Useful helpers that proved reusable:
- `humanizeProjectStatus`
- `humanizeApprovalState`
- `humanizeTaskStatus`
- `humanizeEventType`
- `humanizeOwnerRole`
- `summarizeProjectCard`
- `summarizeProjectNeed`
- `summarizeApprovalRisk`
- `summarizeApprovalRecommendation`
- `summarizeTask`
- `summarizeEvent`
- `bossHeroFromProject`

Why this mattered:
- it stopped engineering wording from leaking back into the UI during later edits
- it made `ControlCenterPage.tsx`, `ProjectsPage.tsx`, and `ApprovalsPage.tsx` converge toward the same boss-language
- it made later polish much faster because wording changes happened in one place

Rule of thumb:
- if a page needs to show status, event, task, owner, or recommendation text, route it through the translation layer first
- treat raw internal values as implementation detail that should stay in second-level detail panes

## 11. `/projects/[id]` should be a decision board first, not a task inspector first
A useful product-level lesson from the project-page rewrite:

The first screen should answer four boss questions immediately:
- 這案現在往哪裡走
- 現在卡在哪裡
- 下一個決策是什麼
- 我現在最該按哪個動作

A working layout pattern was:
- Hero block:
  - title
  - `phase_goal`
  - `next_action_summary`
- Three summary cards:
  - 目前方向
  - 目前卡點
  - 下一個決策
- Right-side primary action block:
  - 你現在最該做什麼
- Embedded mini decision workspace for pending approvals
- Only below that: manager-readable task/timeline detail

This sequence worked better than leading with raw task lists, event tables, or engineering activity streams.

Practical rule:
- first screen = decision and exception management
- lower sections = audit trail, tasks, recent events, raw metadata

## 12. Extend `/sessions` into a real operator workbench, not just a transcript viewer
A high-value finishing step for the 9119 control plane was upgrading the web conversation page so it stops feeling like raw chat history.

Useful backend pattern:
- keep `task_charter` on `GET /api/sessions/{id}`
- derive it from actual message flow plus session-tracking signals
- include not only:
  - `goal`
  - `owner`
  - `status`
  - `next_step`
- but also:
  - `decision_state`
  - `recent_step`
  - `stage`
  - `blocker`
  - `latest_user_request`
  - `latest_reply`
  - `last_tool`

This let the frontend render a real workbench answering:
- 這段交辦現在最重要的是什麼
- 最近做到哪一步
- 有沒有卡點
- 下一步是什麼
- 這輪成功定義是什麼

Useful frontend pattern in `web/src/pages/SessionsPage.tsx`:
- make the charter the first panel above message history
- use a hero-style summary first, then 3–4 operator cards
- show:
  - 目前狀態
  - 最近一步
  - 目前卡點
  - 下一步
- then secondary context:
  - 成功定義
  - 你剛剛交辦什麼
  - Hermes 最新回覆

This is what moved the page from "chat log" to "作業面".

## 13. Filter cron noise out of the main web conversation list
A real product issue emerged after the rest of the dashboard became useful:
- the `/sessions` page was dominated by cron conversations
- operator-facing sessions were pushed down
- the page looked busy but not useful

Working rule:
- on the web conversation list, prefer non-`cron` sessions by default
- if any operator sessions exist, show those first and suppress cron rows from the primary list
- only fall back to cron-heavy results when there are no operator sessions available

This keeps the main conversation page aligned with the boss/operator workflow instead of becoming a scheduler dump.

Also add a short explanatory line such as:
- `這裡優先顯示你真的在操作的對話；背景排程不會洗版。`

Testing lesson:
- when verifying this behavior, patch `_project_db()` in the control-center test if needed so existing local project runtime rows do not override the intended session-selection assertions
- otherwise a locally populated project ledger can make `top_goals` choose project-linked session ids instead of the mocked operator session

## 14. Very important operational lesson: ignore stale background watch notifications after verifying live health

## 14.1 Source-vs-live divergence warning for the 9119 dashboard
A high-cost failure mode showed up while iterating on the built-in dashboard:
- the currently running 9119 dashboard can be newer or behaviorally richer than the `hermes_cli/web_server.py` file on disk
- this can happen after interrupted edits, partial reverts, or recovery attempts where a file is rolled back but an already-running process still serves the more advanced behavior
- if you assume the file on disk is the whole truth, you can accidentally regress a working live control plane by doing a blind `git checkout -- hermes_cli/web_server.py`

Required diagnosis pattern before rollback:
1. verify the live page at `http://127.0.0.1:9119/`
2. verify live JSON from `/api/control-center`
3. compare what the live UI/API exposes against what the source file currently defines
4. only then decide whether you are fixing source drift, process drift, or both

Practical rule:
- when the live dashboard already shows the desired surface, treat that as important evidence
- do not destroy working operator-visible behavior just because the source file looks older or incomplete
- recover the source carefully, then re-verify the live page and API

## 14.2 Self-evolution panel: minimum viable integration pattern
A reusable low-risk pattern worked for surfacing Hermes self-evolution inside the control center without inventing new storage:
- source `self_evolution_status` from wiki:
  - `/Users/brian/wiki/operations/hermes-self-evolution-status.md`
- source `self_evolution_queue` from wiki:
  - `/Users/brian/wiki/operations/hermes-self-evolution-candidate-queue.md`
- source `self_evolution_cron_jobs` by filtering cron jobs whose names include `self-evolution`

Good payload additions to `/api/control-center`:
- `self_evolution_status`
- `self_evolution_queue`
- `self_evolution_cron_jobs`

Good boss-mode cards on `ControlCenterPage.tsx`:
- one summary card for:
  - current focus
  - last reviewed at
  - candidate count
  - next scheduled run
  - latest deferred items
- one action/inspection card for:
  - top current candidate
  - latest accepted learnings

Why this worked:
- it reused the wiki + cron assets already maintained by the self-evolution loop
- it created immediate user-visible value on 9119
- it avoided premature schema expansion

## 14.3 Completion standard for this slice
Do not mark the self-evolution dashboard slice complete just because files changed.
Require both:
1. the 9119 homepage visibly shows the new self-evolution blocks
2. `/api/control-center` returns all three keys:
   - `self_evolution_status`
   - `self_evolution_queue`
   - `self_evolution_cron_jobs`

A good live proof shape was:
- focus count > 0
- candidate count > 0
- cron count > 0

Only after both page-level and API-level proof should this slice be considered done.
Real repeated failure mode during dashboard iteration:
- old background `terminal(background=true)` sessions keep emitting delayed watch notifications
- they may say:
  - `Hermes Web UI → http://127.0.0.1:9119`
  - `ERROR`
  - `address already in use`
  - process completed exit 137
- these can appear long after a newer dashboard instance is already healthy

Do NOT treat each notification as the current truth.

Reliable diagnosis pattern:
1. check the real listener:
   - `lsof -nP -iTCP:9119 -sTCP:LISTEN`
2. check a live JSON API endpoint, not just the page shell:
   - `/api/projects`
   - `/api/autopilot/driver`
3. if the live listener and APIs are healthy, treat the old notifications as stale noise

This was essential to avoid getting dragged off the main implementation line by obsolete watch events.

## Verification workflow that worked

Backend tests:
- `source venv/bin/activate && python -m pytest tests/hermes_cli/test_web_server.py -q`

Frontend build:
- `cd web && npm run build`

Live checks:
- `curl -s -D - http://127.0.0.1:9119/api/projects | head -n 40`
- `curl -s -D - http://127.0.0.1:9119/api/approvals | head -n 40`
- `curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 40`

Background-push latency check:
- measure `POST /api/projects/{id}/push`
- good result was ~0.01s after converting it to queue-and-return

Autopilot proof:
1. call `GET /api/autopilot/driver`
2. call `POST /api/autopilot/driver` with `manual_verify`
3. wait > interval
4. call `GET /api/autopilot/driver` again
5. confirm `last_cycle_at` advanced automatically

Noop proof:
- create a pending approval on a project
- run manual driver cycle
- expect:
  - `noop_already_waiting_on_human_approval`
  - no fake transition counts

Writeback proof:
- review endpoint changes task status
- verify endpoint writes `verification-report`
- escalate endpoint blocks project/task
- detail endpoint reflects all of these in `recent_events`

Reusable one-click smoke command:
- `source venv/bin/activate && python scripts/project_writeback_live_smoke.py`
- the script creates a throwaway verification project, pauses its autopilot by default, runs review/verify/escalate, fetches detail, asserts the final writeback shape, and prints JSON
- good live result should include:
  - `review_task_status == review_passed`
  - `verify_artifact_type == verification-report`
  - `final_project_status == blocked`
  - `recent_event_types` containing `review_decided`, `artifact_written`, `verification_recorded`, `escalation_raised`

Live-check discipline learned in practice:
1. choose a dedicated throwaway verification project
2. pause that project's autopilot first so background pushes do not race your manual writeback checks
3. trigger review / verify / escalate from the live `/projects` embedded project workspace, not only via curl
4. verify both surfaces:
   - UI detail pane updates status / blocker text / recent activity immediately
   - `GET /api/projects/{id}` shows changed `status`, `waiting_reason`, task status, `output_artifact_id`, and latest event sequence
5. after escalation, expect the project to end in `blocked`; this is the intended final state for the live check, not a failure of the test


Live-check note learned in practice:
- current `GET /api/projects/{id}` detail reliably exposes `tasks`, `approvals`, and `recent_events`
- it may not expose a populated `artifacts` list even when `record_verification()` has already created the artifact row
- endpoint response shapes are asymmetric, so do not assume every writeback call returns a top-level `event`
  - `POST /api/projects/{id}/review` reliably returns `ok`, `task`, and `project`
Live-check note learned in practice:
- current `GET /api/projects/{id}` detail returns the project fields at the top level, with `tasks`, `approvals`, and `recent_events` as sibling keys; do not assume a nested `{ "project": ... }` wrapper
- it may not expose a populated `artifacts` list even when `record_verification()` has already created the artifact row
- so for live proof of verify writeback, check all three:
  - `POST /api/projects/{id}/verify` returns `artifact.artifact_type == verification-report`
  - project detail shows `verification_recorded` and `artifact_written`
  - task/output linkage or task status changed as expected
- for the dedicated UI control live check, the expected end state after clicking all three workspace buttons is `blocked`; that is success for the exercise, not a regression


## Pitfalls
- Do not rely on transcript/session heuristics as the primary source of project truth
- Do not block the UI while a full project push runs
- Do not count repeated pending-approval normalization as progress
- Do not chase every old background-process watch notification; verify the live listener and API first
- After backend changes, restart the dashboard process bound to 9119 and re-check the real listener
- For the dashboard, user-visible value comes from a clean control plane and decision language, not from exposing more internal state names

## Good stopping point
A strong first milestone is reached when:
- the user can open 9119
- create a project
- push it without UI freezing
- see pending approvals
- decide approvals
- inspect autopilot status
- verify review/verify/escalate writes are reflected in the project detail view

At that point the dashboard has crossed from "monitoring shell" into a real project/agent control surface.
