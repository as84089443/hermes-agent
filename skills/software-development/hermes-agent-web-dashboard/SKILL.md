---
name: hermes-agent-web-dashboard
description: Launch and verify Hermes Agent's built-in web dashboard (config/API keys/sessions UI), including frontend build behavior, local health checks, and optional temporary public exposure via localhost.run.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, web-ui, dashboard, fastapi, vite, localhost-run]
---

# Hermes Agent Web Dashboard

Use when the user asks whether Hermes Agent itself has a web UI, or wants the built-in Hermes dashboard running locally.

## What this is

This is the built-in Hermes Agent management dashboard, not Hermes Workspace.

It is for:
- configuration management
- API key / env management
- monitoring active and recent sessions

It is NOT the full workspace-style UI with chat/files/terminal/memory/skills all in one shell.

## Key finding

The actual CLI command is:

```bash
python -m hermes_cli.main dashboard --no-open --port 9119
```

Important: the code path in `hermes_cli/main.py` registers the `dashboard` command.
A README may mention `web`, but the reliable current command is `dashboard`.

## Prerequisites

From the Hermes repo root:
- activate the venv first
- ensure FastAPI + uvicorn are installed in the venv
- ensure `web/` frontend deps can be installed with npm

## Local launch workflow

### 1. Check frontend/backend prerequisites

```bash
cd /path/to/hermes-agent
source venv/bin/activate
python -m pip show fastapi uvicorn
cd web && npm install
```

### 2. Start the dashboard server

```bash
cd /path/to/hermes-agent
source venv/bin/activate
python -m hermes_cli.main dashboard --no-open --port 9119
```

The command auto-builds the `web/` frontend if npm is available.

### 3. Verify locally

Use GET, not HEAD, for the root page check.

```bash
curl -s http://127.0.0.1:9119/ | head -n 20
```

Expected:
- HTML with `<title>Hermes Agent</title>`
- built assets under `/assets/...`

Note: `curl -I` or HEAD can return `405 Method Not Allowed` depending on route handling. That does not necessarily mean the UI is broken. Use a normal GET to verify the page.

## Optional temporary public exposure

If the user wants to preview the Hermes dashboard remotely and no stable deployment exists yet:

```bash
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:9119 nokey@localhost.run
```

Watch the output for:

```text
https://<random>.lhr.life
```

Then verify:

```bash
curl -s https://<random>.lhr.life/ | head -n 20
```

If the HTML loads, the dashboard is reachable publicly.

## Verification checklist

- venv activated
- `fastapi` and `uvicorn` present
- `web/` dependencies installed
- dashboard command starts without import errors
- local GET on `http://127.0.0.1:9119/` returns HTML
- optional localhost.run tunnel returns the same HTML externally

## Localization finding

The built-in Hermes Agent dashboard can be partially localized to Traditional Chinese, but do it surgically.

Safe first pass:
- localize top-level shell labels in `web/src/App.tsx`
  - nav labels (`Status`, `Sessions`, `Analytics`, `Logs`, `Cron`, `Skills`, `Config`, `Keys`)
  - small shell chrome like `Web UI`
- rebuild with `cd web && npm run build`
- verify the dashboard still loads through the running FastAPI server

Safe second pass:
- translate only obvious user-facing string literals inside specific pages, starting with:
  - `web/src/pages/StatusPage.tsx`
  - `web/src/pages/SessionsPage.tsx`
  - `web/src/pages/LogsPage.tsx`
  - `web/src/pages/AnalyticsPage.tsx`
  - `web/src/pages/CronPage.tsx`
  - then small, low-risk copy blocks in `EnvPage.tsx` / `ConfigPage.tsx`
- examples of safer targets:
  - card titles (`Active Sessions`, `Recent Sessions`, `Connected Platforms`)
  - status labels (`Connected`, `Disconnected`, `Running`, `Stopped`)
  - placeholders and empty-state text (`Search message content...`, `No sessions yet`)
  - table headers / filter labels / toast text in logs, analytics, and cron pages
  - explanatory paragraphs and button labels in the env/config pages
- rebuild after each page or small batch, not after a giant translation sweep

Important warning:
- do NOT run blind global search/replace across page source files
- naive replacements can corrupt:
  - imported symbol names (e.g. Lucide icons like `Settings`, `Save`, `FileText`)
  - TypeScript types and generics (`SetStateAction`, `ComponentType`, imported API types)
  - method names on the API client (`getSessions`, `getLogs`, `getAnalytics`)
  - built-in JavaScript / Date methods such as `toLocaleString()` if text replacement is too broad
  - component imports like `Input`, `FormInput`, `Settings2`, `Save`
- if you want full Traditional Chinese localization, translate user-facing string literals page-by-page, not identifiers
- always run `cd web && npm run build` after each page or small batch; do not queue a large unverified translation pass
- if a page-level localization pass breaks TypeScript, immediately restore or surgically fix the affected file and rebuild before trying a narrower patch
- a real failure mode already observed: replacing text too broadly in `CronPage.tsx` mutated `toLocaleString()` into an invalid identifier; the safe recovery was to restore the method name exactly and rebuild
- another real failure mode: broad replacements in `EnvPage.tsx` can mutate imported symbols (`Settings`, `Save`) and type names (`SetStateAction`) because those English words appear in identifiers, not just UI copy. If that happens, immediately restore the file from git and re-apply only targeted literal-string patches.
- in practice, `StatusPage`, `SessionsPage`, `LogsPage`, `AnalyticsPage`, and `CronPage` were good candidates for visible, low-risk localization; `EnvPage` / `ConfigPage` still require a more conservative pass

## Env/Keys page localization finding
For the dashboard's Keys/Env page, not all visible English comes from `web/src/pages/EnvPage.tsx`.

Important source split:
- page chrome / buttons / counts live in `web/src/pages/EnvPage.tsx`
- many provider/tool descriptions come from backend metadata in `hermes_cli/config.py` under `OPTIONAL_ENV_VARS`

Implication:
- if the page still shows English descriptions like Telegram/Slack token help text after translating the React component, patch the corresponding `OPTIONAL_ENV_VARS[KEY]["description"]` strings in `hermes_cli/config.py`
- then restart the dashboard server so the backend API serves the updated metadata
- verify against the live page, not just the source diff

Safe workflow for Keys/Env page:
1. patch visible count/section strings in `EnvPage.tsx`
2. patch provider/tool description strings in `hermes_cli/config.py` for the specific env vars that are visibly exposed
3. restart `python -m hermes_cli.main dashboard --no-open --port 9119`
4. verify on the live tunnel/local page that the rendered descriptions changed

High-value first targets actually seen in the UI:
- `TELEGRAM_BOT_TOKEN`
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

- another real failure mode: broad replacements in `EnvPage.tsx` mutated identifiers like `Settings`, `Save`, and `SetStateAction`; the safe recovery was `git restore --source=HEAD -- web/src/pages/EnvPage.tsx`, then re-apply only targeted literal-string patches and rebuild
- in practice, `StatusPage`, `SessionsPage`, `LogsPage`, `AnalyticsPage`, and `CronPage` were good candidates for visible, low-risk localization; `EnvPage` / `ConfigPage` still require a more conservative pass

## Web chat surface finding

The built-in Hermes dashboard is no longer only for config / env / monitoring.
It can now serve as a lightweight web chat surface for Hermes itself.

What was added:
- backend route: `/api/chat/send`
- frontend page: the `對話` page (formerly sessions/history only) now supports:
  - starting a new conversation
  - continuing an existing session
  - sending a message directly to Hermes
  - seeing the reply in the same page

Implementation pattern that worked:
1. Reuse the existing session/history infrastructure instead of inventing a separate chat stack.
2. On the backend, create an `AIAgent` with a real `session_id` and shared `SessionDB`.
3. For existing sessions, load `db.get_messages_as_conversation(session_id)` before `run_conversation()`.
4. For new conversations, mint a new `web_<timestamp>_<token>` session id.
5. Return `session_id`, `final_response`, and token usage from `/api/chat/send`.
6. On the frontend, after send:
   - keep or update the selected `session_id`
   - reload `/api/sessions/{id}/messages`
   - reload the session list so the active conversation appears at the top

Why this matters:
- avoids duplicating transcript persistence
- keeps web chat and CLI/gateway history in the same session database model
- makes the dashboard immediately useful as an operator surface, not just a status panel

Current UX level:
- request/response chat works
- session continuation works
- enter-to-send works
- live page verification succeeded

Still a good next step later:
- add streaming token updates and tool-progress visualization so the web chat feels more like the terminal

## Control center tracking finding

A useful boss-mode upgrade is not just showing the global phase.
Operators also need per-conversation tracking.

What worked:
- extend `/api/control-center` with `tracked_sessions`
- derive a lightweight tracking summary from the latest messages in each session
- show for each conversation:
  - `decision_state` (e.g. `進行中`, `需要你介入`, `可追蹤`)
  - `stage` (e.g. `等待 Hermes 接手`, `正在處理中`, `本輪已有回覆`)
  - `recent_step`
  - `latest_user_request`
  - `latest_reply`
  - `attention` if a recent message implies human intervention / risk / blockage
- from the control center card, provide a direct `打開` action that jumps to the corresponding conversation in the `對話` page

Important product lesson:
- a control center that only shows session names is not enough
- translating conversation state into boss-mode progress language is much more valuable than exposing raw IDs or internal event names

### Push-forward button reliability finding

A real control-center failure mode:
- the `往下推進` button can be technically wired correctly, but still feel broken to the user
- common causes are not the click handler itself, but bad session targeting and weak visible feedback

Failure modes seen in practice:
1. the button successfully calls `/api/chat/send`, but the resulting dashboard change is so subtle that the user perceives "nothing happened"
2. the top-goal button binds to `tracked_sessions[0]`, which may be the wrong session
3. the tracked-session list can be polluted by many recent cron sessions, causing the control center to miss the real operator conversation
4. the selected session can be a newly created or empty session (`message_count == 0`), which makes `push forward` look hung or meaningless
5. the selected session may already be actively processing tool calls / subagents, so allowing another push creates a misleading "I clicked it and it froze" feeling

Reliable fixes that worked:
- do NOT bind the top-goal push-forward action to `tracked_sessions[0]` blindly
- introduce a helper that selects the primary goal session by preferring sessions with:
  - `message_count > 0`
  - meaningful `latest_user_request` / `latest_reply` / `attention`
- when populating `/api/control-center`, fetch a wider recent session window (for example 50 instead of 10) before filtering out cron sessions
- build `active_sessions` and `recent_sessions` from operator sessions only, not the raw full list
- if a tracked session is already in `stage == "正在處理中"`, disable push-forward buttons and label them with a status like `Hermes 處理中…`
- keep a visible result surface after a successful push-forward, such as a prominent card showing:
  - what scope was advanced
  - when it completed
  - the first meaningful line of the assistant's new reply
  - a direct `打開完整對話` action

Verification pattern:
1. reproduce in the live browser — verify whether the button changes to `推進中…` / `Hermes 處理中…`
2. test the backing API directly with the same `session_id` via `POST /api/chat/send`
3. inspect `/api/control-center` JSON before and after to confirm:
   - `top_goals[0].session_id`
   - `tracked_sessions`
   - `stage`
   - `message_count`
   - `latest_reply`
4. if the UI still looks stale, verify the live dashboard is serving the new built asset hash from `hermes_cli/web_dist/assets/...`
5. restart the dashboard only after confirming the bound port listener and asset hash, not just because a watch-pattern message appeared

Product lesson:
- for boss-mode controls, correctness alone is not enough
- the operator must be able to perceive that something changed
- a button that works but targets the wrong session, or works without strong feedback, is effectively broken UX

## Runtime/API verification finding

A real failure mode observed during dashboard extension work:
- the frontend shell can look updated while a newly added backend API route is still missing at runtime
- symptom: the new page renders navigation and a loading spinner, but the page body never resolves
- direct API probe for the new route returns the SPA fallback HTML (`index.html`) instead of JSON

This usually means the dashboard server process is still running old backend code and has not been restarted after editing `hermes_cli/web_server.py`.

## Web chat extension finding

The built-in dashboard can be extended from a read-only session browser into a usable web chat surface without building a separate app.

Reusable approach:
- reuse the existing `SessionsPage.tsx` as the conversation shell instead of creating a brand-new page
- keep the existing session history path:
  - `GET /api/sessions`
  - `GET /api/sessions/{session_id}/messages`
- add one minimal write endpoint in `hermes_cli/web_server.py`:
  - `POST /api/chat/send`
- have that endpoint:
  1. resolve or create a `session_id`
  2. load prior conversation via `SessionDB.get_messages_as_conversation(session_id)`
  3. create `AIAgent` using the same runtime/model/toolset resolution pattern used by the API server gateway path
  4. call `agent.run_conversation(...)`
  5. return `{session_id, final_response, usage}`
- then in the frontend:
  - submit the draft to `/api/chat/send`
  - refresh the session message list from `/api/sessions/{session_id}/messages`
  - refresh the session list from `/api/sessions`
  - preserve the returned `session_id` so follow-up turns continue the same conversation

Why this is high leverage:
- no need to invent a second persistence model
- session continuity already works because Hermes writes to the existing session DB
- old conversations and new web-origin turns appear in one unified history surface
- the page can support both "new conversation" and "continue selected session" with very little backend surface area

Recommended first-pass UX:
- rename nav copy from `會話` to `對話`
- keep a two-pane layout:
  - left: searchable session list
  - right: current conversation + compose box
- support `Enter` to send and `Shift+Enter` for newline
- show a simple `Hermes 思考中` badge while waiting

Verification pattern for this feature:
1. add/patch backend tests in `tests/hermes_cli/test_web_server.py` for:
   - successful `POST /api/chat/send`
   - empty message rejection
2. run:
   - `source venv/bin/activate && python -m pytest tests/hermes_cli/test_web_server.py -q`
3. rebuild frontend:
   - `cd web && npm run build`
4. restart the dashboard server
5. verify both:
   - direct API call to `/api/chat/send` returns JSON with `session_id` and `final_response`
   - browser UI can submit a message and render the assistant reply in the selected conversation

Important operational pitfall:
- killing the tracked background launcher process may NOT free port `9119`
- a child `python` process can remain bound to the port after the original background session exits or is killed
## Runtime/API verification finding

A real failure mode observed during dashboard extension work:
- the frontend shell can look updated while a newly added backend API route is still missing at runtime
- symptom: the new page renders navigation and a loading spinner, but the page body never resolves
- direct API probe for the new route returns the SPA fallback HTML (`index.html`) instead of JSON

This usually means the dashboard server process is still running old backend code and has not been restarted after editing `hermes_cli/web_server.py`.

Reliable diagnosis pattern:
1. verify the page shell loads in the browser
2. `curl -s -D - http://127.0.0.1:9119/<new-api-route> | head -n 40`
3. if `content-type` is `application/json`, the route is live
4. if you get HTML with the SPA app shell instead, the route is not registered in the running server process
5. compare against an existing known-good endpoint like `/api/status` to distinguish "server is up" from "new route is missing"

Additional real-world pitfall:
- killing the tracked background launcher process is not always enough
- the actual listener on port 9119 may be a lingering child Python process that keeps the port bound
- symptom: new dashboard launches print `Hermes Web UI → http://127.0.0.1:9119` and then fail with `address already in use`, even though the prior tracked process shows exited/killed
- reliable recovery:
  1. `process(action='list')` to see launcher sessions
  2. `lsof -nP -iTCP:9119 -sTCP:LISTEN` to find the real listener PID
  3. kill that PID directly if needed
  4. relaunch dashboard and re-check with both browser and `lsof`

Additional boss-mode control-center finding:
- if `/api/control-center` surfaces raw cron/system transcripts, `[SILENT]`, or traceback JSON as operator-facing cards, the page becomes unreadable for decision-makers
- tracked session summaries should filter or humanize these before display
- specifically exclude or down-rank:
  - `source='cron'` sessions in the main tracked-session area
  - messages starting with `[SYSTEM:`
  - `[SILENT]`
  - raw traceback / JSON error blobs
- replace raw execution errors with short operator language such as: `這段工作最近執行失敗，值得檢查或重新推進。`

Recovery pattern:
- stop the old process bound to port 9119
- restart with:

```bash
source venv/bin/activate
python -m hermes_cli.main dashboard --no-open --port 9119
```

Then re-verify both:
- `GET /api/<new-route>` returns JSON, not HTML
- browser page content appears instead of a perpetual spinner

Additional process pitfall learned in practice:
- killing the tracked background session may NOT free port 9119 if a child Python process remains alive
- symptom: the background session shows exited/killed, but `lsof -nP -iTCP:9119 -sTCP:LISTEN` still shows a listener PID and new dashboard launches fail with `address already in use`

Reliable cleanup pattern:
1. inspect the real listener:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
```

2. if a stale listener remains, kill the actual PID, not just the tracked session:

```bash
kill -9 <listener-pid>
```

3. restart the dashboard only after `lsof` shows no listener on 9119

Another real-world pitfall:
- old background launcher sessions can keep emitting delayed `watch_patterns` notifications like `Hermes Web UI`, `ERROR`, or `completed (exit 137/143)` long after a newer 9119 server is already healthy
- these stale alerts are easy to misread as current production failures

Current implementation note:
- `ProcessRegistry.recover_from_checkpoint()` now recovers detached processes for management only
- it intentionally does NOT restore `notify_on_complete`, `watch_patterns`, or gateway watcher re-enqueue on recovered processes
- reason: after restart, the original output stream/context is gone, so auto-resuming notifications for old processes creates stale chat noise instead of useful signal
- practical effect: recovered old dashboard/server jobs still appear in `process(list)` and can be killed/polled, but they will not auto-push completion/watch messages back to the user anymore

Reliable interpretation rule:
1. do NOT trust the old process notification by itself
2. verify the live listener and API health first:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
curl -s -D - http://127.0.0.1:9119/api/status | head -n 20
curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 20
```

3. if a current listener exists and live APIs return `200 OK`, treat the old notification as stale background noise, not a blocker
4. only take action if the current listener is missing or the live API health check fails

This matters when many dashboard restarts happen in one session: the correct move is to ground on the current listener/API state, not on delayed notifications from dead processes.

- these alerts may arrive long after a newer healthy dashboard process is already serving 9119
- do NOT treat those alerts as current truth without checking the live listener and a real JSON API

Reliable verification pattern when stale alerts appear:
1. confirm the real listener PID:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
```

2. probe a real JSON endpoint, not just `/`:

```bash
curl -s -D - http://127.0.0.1:9119/api/status | head -n 30
curl -s -D - http://127.0.0.1:9119/api/projects | head -n 30
```

3. if the current listener is healthy and the API returns 200 JSON, treat old process notifications as stale noise and keep the main work moving

## Project-control-plane push action finding

When extending the Hermes dashboard into a real project control plane, a `push project forward` action must NOT block the HTTP request until the whole agent run finishes.

Observed failure mode:
- clicking `往下推進` looked like the site froze
- root cause: the endpoint synchronously waited for `AIAgent.run_conversation(...)` to finish
- user-visible effect: the UI felt hung even though work was still progressing

Better pattern that worked:
- `POST /api/projects/{id}/push` should:
  1. mark the project/task as `running`
  2. enqueue the real push as a background asyncio task
  3. return immediately with `{ ok: true, queued: true, project: ... }`
- then let the frontend poll the normal project/control-center APIs for state changes

Important companion rule:
- if a project is already `waiting_on_human` or has pending approvals, return a noop-style status instead of re-running the same push and overstating progress
- this keeps the dashboard honest and prevents fake movement

## Progress-visibility finding for boss-mode work

A separate real failure mode: the agent may be actively making progress, but the user cannot see it from the dashboard because the control center only shows static phase summaries.

When the user says some version of:
- "我這邊沒有看到你的進度"
- "I can’t tell what you’re actually working on"
- "I can see the phase, but not the real build tasks"

Do NOT respond with prose alone.
Expose the live implementation work as first-class dashboard data.

Reliable pattern that worked:
1. create a dedicated execution-status artifact in the wiki, separate from the high-level live-status page
   - example path:
     `~/wiki/concepts/hermes-ai-company-phase1-execution-status.md`
2. store:
   - `Current Goal`
   - `Implementation Tasks`
   - one task per bullet with `[in_progress] / [pending] / [completed]`
   - per-task `now`, `next`, and `verify` lines
3. parse that artifact in `hermes_cli/web_server.py`
4. return structured fields from `/api/control-center`, for example:
   - `execution`
   - `top_goals`
   - `implementation_tasks`
   - `boss_decisions`
5. render those fields in the dashboard homepage as visible cards, not buried in a text paragraph

Recommended homepage sections for this pattern:
- `目前目標`
- `正在落地的 implementation tasks`
- `等你拍板`

Important product lesson:
- a high-level `current phase` card is not enough for users who want to supervise autonomous execution
## Port-9119 lingering child-process finding

A real operational failure mode observed during repeated dashboard restarts:
- killing the tracked background session is sometimes NOT enough to free port 9119
- the parent shell/background job may exit, but the actual Python listener child can remain alive and keep the port bound
- symptom:
Additional process pitfall learned in practice:
- killing the tracked background session may NOT free port 9119 if a child Python process remains alive
- symptom: the background session shows exited/killed, but `lsof -nP -iTCP:9119 -sTCP:LISTEN` still shows a listener PID and new dashboard launches fail with `address already in use`

Reliable cleanup pattern:
1. inspect the real listener:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
```

2. if a stale listener remains, kill the actual PID, not just the tracked session:

```bash
kill -9 <listener-pid>
```

3. restart the dashboard only after `lsof` shows no listener on 9119

Another real-world pitfall:
- old background launcher sessions can keep emitting delayed `watch_patterns` notifications like `Hermes Web UI`, `ERROR`, or `completed (exit 137/143)` long after a newer 9119 server is already healthy
- these stale alerts are easy to misread as current production failures

Current implementation note:
- `ProcessRegistry.recover_from_checkpoint()` now recovers detached processes for management only
- it intentionally does NOT restore `notify_on_complete`, `watch_patterns`, or gateway watcher re-enqueue on recovered processes
- reason: after restart, the original output stream/context is gone, so auto-resuming notifications for old processes creates stale chat noise instead of useful signal
- practical effect: recovered old dashboard/server jobs still appear in `process(list)` and can be killed/polled, but they will not auto-push completion/watch messages back to the user anymore

Reliable interpretation rule:
1. do NOT trust the old process notification by itself
2. verify the live listener and API health first:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
curl -s -D - http://127.0.0.1:9119/api/status | head -n 20
curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 20
```

3. if a current listener exists and live APIs return `200 OK`, treat the old notification as stale background noise, not a blocker
4. only take action if the current listener is missing or the live API health check fails

This matters when many dashboard restarts happen in one session: the correct move is to ground on the current listener/API state, not on delayed notifications from dead processes.

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN || true
```

4. start the dashboard again and re-check the listener PID

This matters because watch-pattern notifications can arrive from stale sessions and make it look like the newest process owns the port when it does not.

## Stale background-process notification finding

Another real operational pitfall during iterative dashboard work:
- old background launcher sessions can continue emitting delayed watch notifications long after a newer healthy dashboard process is already serving 9119
- examples:
  - old sessions report `Hermes Web UI → http://127.0.0.1:9119`
  - then later report `ERROR`, `address already in use`, or exit `137`
  - the UI and APIs may still be healthy because a newer listener is already running

Important rule:
- do NOT treat these stale notifications as proof the current dashboard is broken
- treat them as historical noise until live health checks prove otherwise

Reliable verification pattern:
1. check the real active listener:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
```

2. probe a known JSON endpoint, not just the root HTML:

```bash
curl -s -D - http://127.0.0.1:9119/api/status | head -n 20
curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 20
```

3. if the listener exists and JSON endpoints return `200 OK`, the current dashboard is healthy even if old `process` sessions keep surfacing stale `Hermes Web UI` / `ERROR` / `exit 137` notifications

Short operator conclusion to use:
- `這是舊背景程序的延遲通知，不是現在的 live 故障。先看目前 9119 的 listener 與 API 健康，不要被舊 watch 噪音帶偏。`

## Project push endpoint finding

When extending the dashboard into a real project control plane, a naive `POST /api/projects/{id}/push` implementation can make the web UI look frozen even when the backend is technically working.

Observed failure mode:
- the endpoint waits synchronously for a full agent run to complete
- the button stays in a pending state for a long time
- users perceive this as `網站卡住了`

Better pattern that worked:
- queue the project push in the background
- return immediately with a lightweight `{ok, queued, project}` response
- update project state first to something like `running`
- let the page poll project detail / control-center state for follow-up updates

Practical implementation shape:
- keep a process-local map of running project push tasks
- when `/push` is called:
  - if the project is already running, return the current project payload immediately
  - otherwise write a `running` summary to the ledger
  - spawn `asyncio.create_task(...)`
  - return immediately
- on task completion or failure, write the result back into the ledger and remove the in-memory running marker

This prevents fake UI hangs and makes the project control page feel responsive even when the actual agent work takes longer.

## Stale watch-notification finding

A recurring operational confusion during dashboard work:
- old background launcher sessions can keep emitting delayed `watch_patterns` notifications long after a newer healthy dashboard instance is already serving 9119
- examples include old sessions surfacing:
  - `Hermes Web UI → http://127.0.0.1:9119`
  - `address already in use`
  - generic `ERROR`
  - eventual `exit code 137`
- these messages may appear in the current chat even though the current live dashboard is healthy

Do NOT treat those notifications as authoritative by themselves.
Always check the live system state directly.

Reliable truth-source pattern:
1. confirm the current listener:

```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
```

2. confirm a live JSON API endpoint, not just the SPA shell:

```bash
curl -s -D - http://127.0.0.1:9119/api/status | head -n 30
curl -s -D - http://127.0.0.1:9119/api/control-center | head -n 40
```

3. if using the newer project-control-plane work, also probe:

```bash
curl -s -D - http://127.0.0.1:9119/api/projects | head -n 30
curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 30
```

Interpretation rule:
- if the current listener exists and live endpoints return `200 OK`, then old watch notifications are stale noise from older launcher sessions and should be ignored
- only treat the system as broken if the live listener or live endpoints fail now

## Push-action UX finding: avoid synchronous long-running HTTP for dashboard controls

A real UX trap when adding project controls to the dashboard:
- if a button like `往下推進` waits synchronously for a full AIAgent run before returning HTTP, the page feels frozen or broken even when work is actually progressing
- users interpret this as the website being stuck

Safer pattern:
- accept the action immediately
- mark the project/task as `running`
- launch the actual work in a background `asyncio.create_task(...)`
- return a fast JSON response such as `{ ok: true, queued: true, project: ... }`
- let the page poll or refresh the project status surface

This worked better for dashboard operator UX because:
- the button becomes responsive
- the control surface can show `running` vs `idle`
- background work can continue without holding the browser request open
- follow-up state is visible through `/api/projects/...` or a driver snapshot endpoint

## Web chat surface finding

The Hermes dashboard is no longer only a config/status viewer. A practical first chat surface can be built by reusing existing session APIs and adding one lightweight send endpoint.

Proven pattern:
- keep session history in the existing session store
- add a simple send endpoint in `hermes_cli/web_server.py` (for example `/api/chat/send`)
- have the frontend send `{message, session_id}`
- after sending, reload the session messages via the existing `/api/sessions/{id}/messages` endpoint instead of building a custom sync protocol first

Why this worked well:
- minimal backend surface area
- preserves conversation continuity with existing session IDs
- lets the web UI become a real conversation workspace before implementing richer streaming UX

Useful UX follow-up that proved valuable:
- allow the control center to store a selected session ID in `localStorage`
- dispatch a lightweight browser event (for example `hermes:navigate`) to switch the app to the conversation page
- auto-open that session when the conversation page loads

This creates a practical boss-mode workflow:
- see a tracked conversation on the control center
- click `打開`
- jump directly into the exact session and continue the work

## Control center tracking finding

A more useful boss-mode control center should not summarize only the global upgrade phase. It should also expose per-conversation tracking cards.

## Project control-plane upgrade finding

The built-in Hermes dashboard can be pushed beyond session monitoring into a real project-control front door by adding a separate persisted project ledger instead of deriving everything from session transcripts or wiki markdown.

What worked:
- add a lightweight SQLite-backed runtime ledger separate from `SessionDB`
- keep the smallest useful entities first:
  - `Project`
  - `Task`
  - `Artifact`
  - `Event`
  - `Approval`
- put this in a dedicated module (for example `hermes_project_state.py`) using `get_hermes_home()` so state lives under the active Hermes profile
- expose project APIs in `hermes_cli/web_server.py`:
  - `GET /api/projects`
  - `POST /api/projects`
  - `GET /api/projects/{id}`
  - `POST /api/projects/{id}/push`
  - `POST /api/projects/{id}/pause`
  - `POST /api/projects/{id}/resume`
  - `POST /api/projects/{id}/approvals/request`
  - `GET /api/approvals`
  - `POST /api/approvals/{id}/decide`
  - optional writeback helpers such as:
    - `POST /api/projects/{id}/review`
    - `POST /api/projects/{id}/verify`
    - `POST /api/projects/{id}/escalate`
- extend the frontend API client (`web/src/lib/api.ts`) first, then add pages/components
- add dedicated pages like:
  - `web/src/pages/ProjectsPage.tsx`
  - `web/src/pages/ApprovalsPage.tsx`
- wire those pages into `web/src/App.tsx` navigation instead of overloading only the control center

Important product lesson:
- once project data is real, the control center should prioritize:
  - today’s most important projects
  - pending approvals
  - blockers
  - system-next-step
  - autopilot status
- implementation details, full session tracking, and long engineering lists should be collapsed into a second layer (for example a `details` section), not left on the first screen

## Push-button UX finding: synchronous project push feels "stuck"

A real failure mode observed during the project-control upgrade:
- `POST /api/projects/{id}/push` originally waited for the full agent turn to finish before returning HTTP
- in the browser this looked like the button or page was frozen, even though the system was still working

Reliable fix:
- make project push background-first
- return immediately with `queued: true`
- record a temporary running state in the project ledger first
- launch the real work in an `asyncio.create_task(...)` background job
- let the frontend poll refreshed project status via the normal control-center / project-detail reload path

Pattern that worked in `hermes_cli/web_server.py`:
- keep a process-local map such as `_PROJECT_PUSH_TASKS: Dict[str, asyncio.Task]`
- before launching:
  - check for existing running task for that project
  - write `status='running'` and a boss-readable summary like `Hermes 正在背景推進這個專案…`
- then spawn a background coroutine that calls the real push logic
- on completion/failure:
  - write result back to the project ledger
  - remove the project id from `_PROJECT_PUSH_TASKS`

Why this matters:
- avoids the user believing the site is hung
- matches boss-mode expectations better: the action acknowledges immediately, then the page reflects progress

## Autopilot driver finding for Hermes dashboard

The dashboard can support a simple inspectable project autopilot loop without a separate service first.

What worked:
- keep a small in-process singleton state in `hermes_cli/web_server.py`, for example:
  - `started`
  - `status`
  - `interval_seconds`
  - `last_cycle_at`
  - `last_cycle_reason`
  - `last_summary`
  - `last_error`
- expose:
  - `GET /api/autopilot/driver`
  - `POST /api/autopilot/driver`
- use `POST` for:
  - manual cycle trigger
  - optional `project_ids` filtering
  - optional `stop` control
- start the loop lazily when the control center or project APIs are hit

Critical false-progress guard:
- if a project already has pending approvals or is effectively waiting on the same human gate, return a noop result like:
  - `noop_already_waiting_on_human_approval`
- do not repeatedly rewrite the same blocked/waiting state every interval

Live verification pattern that worked:
1. `GET /api/autopilot/driver` — confirm startup state
2. `POST /api/autopilot/driver` — confirm manual cycle works
3. wait through one real interval
4. `GET` again — confirm `lastCycleAt` advanced automatically
5. confirm `last_error` remains null

## Live browser QA finding for boss-mode cleanup

When reworking the dashboard toward a decision-first front door, the highest-value QA pattern was:
- inspect the home page first as a boss/PM, not as the engineer who built it
- explicitly ask:
  - do I know what to do in 5 seconds?
  - what is the most important project?
  - what needs my decision now?
  - what can be pushed to the second layer?
- then collapse or demote:
  - implementation-task lists
  - verbose session-tracking walls
  - engineering/system-state explanations
- preserve on the first screen only:
  - top projects
  - pending decisions
  - blockers
  - next step
  - autopilot status

## Background-process noise finding

A recurring operational issue during dashboard work:
- old background dashboard launch sessions can keep emitting delayed watch-pattern notifications like:
  - `Hermes Web UI → http://127.0.0.1:9119`
  - `address already in use`
  - random `ERROR` lines
  long after the real live server has been restarted successfully

Important rule:
- treat these as stale alerts unless the current live listener and APIs also fail
- always verify current truth with:
  - `lsof -nP -iTCP:9119 -sTCP:LISTEN`
  - `curl -s -D - http://127.0.0.1:9119/api/<known-route>`
- do not let old process notifications derail the current implementation phase

Good user-facing interpretation:
- an exited old process emitting a delayed watch notification is just historical noise
- the real question is whether the current listener and API are healthy right now

Operator communication rule learned in practice:
- do not proactively report normal dashboard background-process notifications such as successful `Hermes Web UI → http://127.0.0.1:9119` startup lines or routine exit `137/143` / `tcsetattr` cleanup noise
- only interrupt the user when verification shows a real live problem: missing listener, failing JSON API, broken page load, or an actionable error that requires intervention
- if a noisy notification appears, silently verify with `lsof` + a real JSON endpoint first; only surface it if the live checks fail

A reusable minimum card shape that worked well:
- `decision_state` — e.g. `進行中`, `需要你介入`, `可追蹤`
- `stage` — e.g. `等待 Hermes 接手`, `正在處理中`, `本輪已有回覆`
- `recent_step` — the latest meaningful action in human language
- `latest_user_request`
- `latest_reply`
- `attention` — any line suggesting risk, blocker, or need for human intervention

Useful derivation heuristic for v1:
- inspect recent session messages from `SessionDB`
- if the last message is from `user`, treat it as waiting for Hermes
- if the last message is a `tool` result or there are pending tool calls, treat it as processing
- if the last message is an assistant reply, treat it as a completed turn
- scan recent messages for attention keywords (`需要你`, `請決定`, `卡住`, `失敗`, `approval`, etc.) to populate a boss-facing intervention signal

Also useful UX refinement:
- replace a low-value `現在在做什麼` freeform summary block with 2-3 decision cards:
  - `現在最值得你看`
  - `系統正在推進`
  - `系統下一步`

This made the control center feel more like an operator dashboard and less like a wiki excerpt renderer.

## Port-9119 lingering child-process finding

A real operational failure mode observed during repeated dashboard restarts:
- killing the tracked background session is sometimes NOT enough to free port 9119
- the parent shell/background job may exit, but the actual Python listener child can remain alive and keep the port bound
- symptom:
  - new dashboard launch prints `Hermes Web UI → http://127.0.0.1:9119`
  - then immediately fails with `address already in use`
  - `process list` may show the old session as exited, but `lsof -nP -iTCP:9119 -sTCP:LISTEN` still shows a Python PID

Reliable diagnosis pattern:
1. `process(action='list')` to inspect tracked background sessions
2. `lsof -nP -iTCP:9119 -sTCP:LISTEN` to inspect the real listener PID
3. if the tracked session is gone but `lsof` still shows a listener, kill the listener PID directly

Recovery pattern that worked:
```bash
kill -9 <listener-pid>
lsof -nP -iTCP:9119 -sTCP:LISTEN || true
source venv/bin/activate
python -m hermes_cli.main dashboard --no-open --port 9119
```

Important lesson:
- do not trust only the process registry entry when debugging dashboard restarts
- always verify the real bound listener on 9119 before assuming the restart succeeded

## Hermes dashboard project-control-plane finding

The built-in Hermes dashboard can be upgraded from a session/status surface into a usable boss-mode project control plane without building a separate app first.

Reusable minimum architecture that worked:
- add a lightweight persisted ledger module (for example `hermes_project_state.py`) separate from `SessionDB`
- persist at least:
  - `Project`
  - `Task`
  - `Approval`
  - `Event`
- add backend routes in `hermes_cli/web_server.py`:
  - `GET /api/projects`
  - `POST /api/projects`
  - `GET /api/projects/{project_id}`
  - `POST /api/projects/{project_id}/push`
  - `POST /api/projects/{project_id}/pause`
  - `POST /api/projects/{project_id}/resume`
  - `POST /api/projects/{project_id}/approvals/request`
  - `GET /api/approvals`
  - `POST /api/approvals/{approval_id}/decide`
- add frontend pages and nav entries:
  - `web/src/pages/ProjectsPage.tsx`
  - `web/src/pages/ApprovalsPage.tsx`
  - update `web/src/App.tsx`
  - extend `web/src/lib/api.ts`

High-value UX pattern:
- `/projects` should let the user:
  - create a project
  - push next step
  - pause/resume autopilot
  - request an approval
  - inspect task/event history
- `/approvals` should act as a true decision workspace with:
  - 批准
  - 要求修改
  - 拒絕
  - open project

## Important experiential finding: project push must be backgrounded

A real failure mode observed in practice:
- `POST /api/projects/{id}/push` originally awaited a full `AIAgent` turn before returning
- the UI looked frozen because the HTTP request stayed open while the agent worked
- the system was not dead; the endpoint was simply designed as blocking synchronous work

Reliable fix:
- make the push endpoint return immediately
- mark project state as `running`
- launch the actual project push as a background `asyncio.create_task(...)`
- keep a process-global map like `_PROJECT_PUSH_TASKS[project_id]`
- write status back into the project ledger so the UI can poll and render progress

Good pattern:
- immediate response body:
  - `ok: true`
  - `queued: true`
  - latest project snapshot
- background worker later writes:
  - success summary
  - failure summary
  - noop summary
  - session linkage if available

Why this matters:
- prevents the web UI from feeling hung
- gives a usable boss-mode control surface instead of a blocked button
- matches operator expectations for "push/resume" actions

## Autopilot driver finding for Hermes dashboard

A useful next layer on top of project push is a lightweight dashboard-side autopilot driver, even before deeper orchestration exists.

Reusable pattern that worked:
- store singleton driver state in `hermes_cli/web_server.py`, for example:
  - `started`
  - `status`
  - `interval_seconds`
  - `last_cycle_at`
  - `last_cycle_reason`
  - `last_summary`
  - `last_error`
- expose routes:
  - `GET /api/autopilot/driver`
  - `POST /api/autopilot/driver`
- on startup or first control-center load, call a helper like `_ensure_autopilot_driver_started()`
- run a periodic loop with `asyncio.create_task(...)`
- for each cycle:
  - scan projects from the ledger
  - skip terminal projects
  - skip paused projects
  - noop projects already waiting on human approval
  - queue eligible pushes in the background
  - record cycle summary for visibility

Minimum visible verification standard:
- `GET /api/autopilot/driver` returns JSON with live status
- manual `POST` cycle works
- waiting through at least one real interval proves `lastCycleAt` advances automatically

## Critical anti-fake-progress rule

Another real failure mode:
- the autopilot loop can keep touching already-blocked or already-pending projects and appear to be making progress every cycle

Required guard:
- if a project already has pending approval / waiting-on-human state, return a noop result such as:
  - `noop_already_waiting_on_human_approval`
- do not rewrite identical state each interval
- do not treat that as a transition

Why this matters:
- avoids misleading boss-mode dashboards
- prevents event spam
- makes interval summaries trustworthy

## Verification workflow that worked for this upgrade

1. backend tests
```bash
source venv/bin/activate
python -m pytest tests/hermes_cli/test_web_server.py -q
```

2. frontend build
```bash
cd web && npm run build
```

3. verify real API routes, not just the page shell
```bash
curl -s -D - http://127.0.0.1:9119/api/projects | head -n 40
curl -s -D - http://127.0.0.1:9119/api/approvals | head -n 40
curl -s -D - http://127.0.0.1:9119/api/autopilot/driver | head -n 80
```

4. verify push is non-blocking
- measure request time for `POST /api/projects/{id}/push`
- success condition: returns almost immediately with `queued: true`

5. verify interval-based autopilot
- record `lastCycleAt`
- wait through one real interval
- query again and confirm it advanced automatically

## Writeback live-check pattern for review / verify / escalate

When the goal is to prove the project control plane is not just returning `200 OK` but really persisting writeback state, use a three-layer live check:

### Layer 1: verify the live dashboard/API is actually running
```bash
lsof -nP -iTCP:9119 -sTCP:LISTEN
curl -s -D - http://127.0.0.1:9119/api/projects | head -n 40
curl -s -D - http://127.0.0.1:9119/api/status | head -n 40
```

Success condition:
- a real listener exists on `127.0.0.1:9119`
- `/api/projects` returns JSON, not SPA HTML
- `/api/status` confirms the live server is healthy

### Layer 2: run the writeback endpoints against a real project
Pick or create a project, then call:
```bash
curl -s -X POST http://127.0.0.1:9119/api/projects/<project_id>/review \
  -H 'Content-Type: application/json' \
  -d '{"verdict":"PASS","notes":"live check: review writeback pass"}'

curl -s -X POST http://127.0.0.1:9119/api/projects/<project_id>/verify \
  -H 'Content-Type: application/json' \
  -d '{"summary":"live check: verify writeback passed","passed":true}'

curl -s -X POST http://127.0.0.1:9119/api/projects/<project_id>/escalate \
  -H 'Content-Type: application/json' \
  -d '{"reason":"blocker escalation live 驗證"}'
```

Expected state transitions:
- review → task becomes `review_passed`, project returns to `in_progress`
- verify → a `verification-report` artifact is created
- escalate → project becomes `blocked`, with `waiting_reason` populated

### Layer 3: verify the runtime DB directly
Hermes project-control-plane state lives in:
```bash
/Users/<user>/.hermes/project_runtime.db
```
In code this comes from `ProjectStateDB().db_path`; do not guess another filename.

Query all three surfaces:
```bash
python - <<'PY'
import sqlite3, json
conn = sqlite3.connect('/Users/<user>/.hermes/project_runtime.db')
conn.row_factory = sqlite3.Row
project_id = '<project_id>'
print(json.dumps([dict(r) for r in conn.execute(
    'SELECT id, artifact_type, version, status, title, produced_by_task_id FROM artifacts WHERE project_id=? ORDER BY created_at DESC LIMIT 5',
    (project_id,),
).fetchall()], ensure_ascii=False, indent=2))
print('---')
print(json.dumps([dict(r) for r in conn.execute(
    'SELECT id, status, blocking_reason, output_artifact_id, updated_at FROM tasks WHERE project_id=? ORDER BY updated_at DESC LIMIT 5',
    (project_id,),
).fetchall()], ensure_ascii=False, indent=2))
print('---')
print(json.dumps([
    {'event_type': r['event_type'], 'payload': json.loads(r['payload_json']) if r['payload_json'] else None}
    for r in conn.execute(
        'SELECT event_type, payload_json FROM events WHERE project_id=? ORDER BY created_at DESC LIMIT 8',
        (project_id,),
    ).fetchall()
], ensure_ascii=False, indent=2))
PY
```

Success condition:
- `artifacts` contains a new `verification-report`
- `tasks.output_artifact_id` points at that artifact
- latest `events` include `review_decided`, `artifact_written`, `verification_recorded`, and `escalation_raised`

### Final confidence check: targeted pytest
After a successful live check, also run the focused regression test:
```bash
source venv/bin/activate
python -m pytest tests/hermes_cli/test_web_server.py -q -k 'project_review_verify_and_escalate_endpoints'
```

Why this matters:
- live HTTP success alone can mask stale runtime assumptions
- DB verification proves writeback persistence is real
- targeted pytest confirms the intended contract is still covered in-repo

## Pitfalls

- Do not confuse Hermes Agent dashboard with Hermes Workspace
- Do not trust README examples blindly if they say `web`; confirm the actual CLI command in `hermes_cli/main.py`
- Do not use only HEAD/`curl -I` to validate the root page; use GET because HEAD may return 405
- If exposing publicly, tunnel `9119`, not `3000`, unless you intentionally want another app
- Do not mass-translate source code identifiers when localizing the dashboard; only translate visible UI strings incrementally with rebuild checks after each pass
- After adding backend routes in `hermes_cli/web_server.py`, do not assume the running dashboard has picked them up; explicitly probe the new endpoint and restart the dashboard process if it returns SPA HTML instead of JSON
- Do not design project push as a blocking HTTP request if it calls `AIAgent`; the UI will feel frozen even when the system is still working
- Do not claim autopilot works until both manual trigger and interval trigger have been verified live
- Do not count repeated waiting-on-human rewrites as progress; enforce a noop guard

## User-facing summary template

- Hermes Agent itself does have a built-in web dashboard
- local URL: `http://127.0.0.1:9119`
- optional public preview URL if tunnel is active
- this UI is for config / env / session monitoring, not the full workspace shell
