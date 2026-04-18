---
name: ai-department-os-autopilot-driver-loop
description: Build and verify the ai-department-os periodic autopilot driver, including Next.js instrumentation startup, singleton timer guard, live status route, noop de-duplication for pending approvals, and Telegram boss-mode digest notifications.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-department-os, autopilot, nextjs, telegram, scheduler, verification]
---

# ai-department-os Autopilot Driver Loop

## When to use

Use this when working on ai-department-os and you need to:
- turn single-step autopilot ticks into a periodic re-entry loop
- make the loop visible and debuggable in live dev
- prevent fake progress from repeated writes on already-blocked projects
- push boss-mode Telegram summaries from autopilot cycles

This is project-specific to the ai-department-os repo structure and its current state model.

## What worked

### 1. Use a dedicated server-side driver module
Create a separate driver module, not ad-hoc timer logic inside routes.

Recommended file:
- `lib/server/autopilot-driver.ts`

Core responsibilities:
- keep singleton global state on `globalThis`
- track `started`, `status`, `intervalMs`, `lastCycleAt`, `lastCycleReason`, `lastSummary`, `lastError`
- expose:
  - `ensureAutopilotDriverStarted()`
  - `runAutopilotDriverCycle()`
  - `getAutopilotDriverSnapshot()`
  - `stopAutopilotDriver()`

### 2. Start the driver from Next.js instrumentation
Best practical hook found in this repo:
- root `instrumentation.ts`

Pattern:
- import `ensureAutopilotDriverStarted()`
- export `runtime = 'nodejs'`
- in `register()`, guard against non-node runtime and call the start function

This gives a real server-start trigger without inventing a second process first.

### 3. Add a live status + manual kick route
Expose a route for visibility and verification:
- `app/api/autopilot/driver/route.ts`

Recommended behavior:
- `GET` → return driver snapshot
- `POST` → run one cycle and return `{ summary, snapshot }`
- allow request body fields:
  - `reason`
  - `projectIds`
  - `stop`
  - `notifyChatId`

Why this matters:
- you can prove the driver is running
- you can manually force one cycle
- you can verify Telegram digest behavior without waiting for the next interval

### 4. Eligibility rules should be explicit
Inside the driver, scan all projects via:
- `listProjectsRaw()`

Then decide whether each project is eligible.

Useful rules discovered here:
- skip terminal statuses: `completed`, `archived`, `canceled`
- skip `nextAction.notBefore` if it is in the future
- allow `approval_pending`
- allow supported autonomous actions like:
  - `materialize_execution_plan`
  - `execute_task`
- skip other blocking actions

Return per-project result entries with:
- `projectId`
- `outcome` = `advanced | noop | skipped | error`
- `action`
- `reason`

### 5. VERY IMPORTANT: dedupe pending approval normalization
Real failure encountered:
- each interval saw projects already in `approval_pending`
- `autopilotProjectTick()` rewrote the same `await_human_approval` state every cycle
- this created repeated `project_updated` events and fake “progress”

Fix pattern in `lib/server/autopilot.ts`:
- before rewriting pending approval state, detect whether the project is already normalized to the same gate + artifact refs
- if yes, return a noop action such as:
  - `noop_already_waiting_on_human_approval`

Checks that worked:
- `project.status === 'approval_pending'`
- `project.mainPhase === 'human-gate-review'`
- `project.nextAction.type === 'await_human_approval'`
- same `blockingReason`
- same approval artifact refs

This prevents event spam and stops the driver summary from overstating progress.

### 6. Telegram digest integration should reuse existing boss-mode formatting
Do not invent a separate notification tone.
Reuse the project’s Telegram/operator-language style.

Files used:
- `lib/telegram/config.ts`
- `lib/telegram/format.ts`
- `lib/telegram/client.ts`
- new sender helper: `lib/telegram/autopilot.ts`

Useful config sources already present in `.env.local`:
- `TELEGRAM_APPROVAL_CHAT_ID`
- `TELEGRAM_INTAKE_CHAT_ID`
- fallback: first allowed chat if approval chat is unset

### 7. Notification anti-spam rule
Good default behavior:
- normal interval cycles send digest only when:
  - `transitionedProjects > 0`, or
  - `erroredProjects > 0`
- otherwise skip sending

But for live verification, allow explicit override:
- if the request provides `notifyChatId`, force-send the digest even for noop summaries

Why this mattered:
- once most projects were already normalized into `await_human_approval`, almost every manual test was a noop
- without explicit override, you could not prove the Telegram path worked

## Verification workflow that worked

### A. Static checks
Run:
- `npm run typecheck`
- `npm run build`

### B. Live dev checks
Confirm the dev server actually answers:
- `curl -s http://127.0.0.1:3010/settings | head -c 300`

Check driver startup:
- `curl -s http://127.0.0.1:3010/api/autopilot/driver`

Expected signs:
- `started: true`
- interval present
- eventually `lastCycleReason: interval`

### C. Prove periodic behavior
Wait at least one interval, then query again.
Success condition:
- `lastCycleAt` advances automatically
- `lastCycleReason` becomes `interval`

### D. Verify dedupe behavior
POST one known already-pending project:
- expect `transitionedProjects: 0`
- expect action like `noop_already_waiting_on_human_approval`

### E. Verify Telegram digest path
POST with explicit `notifyChatId`:
- if Telegram fails, the route should fail loudly
- if route returns success, the send path likely worked end-to-end

## Known caveat
`next build` may still emit Edge Runtime warnings through the instrumentation import graph because repo server modules use Node APIs.

Important observed reality:
- these were warnings, not build failure
- route/build/runtime still worked
- do not derail the main phase into a large server-boundary refactor unless warnings become blocking

## Good sequence
1. Build singleton periodic driver
2. Expose live status route
3. Verify real interval behavior
4. Fix noop/event spam before trusting summaries
5. Add Telegram digest on top of the verified cycle summary
6. Add forced verify mode for notification testing

## Bad sequence
- adding Telegram notifications before proving the loop actually runs
- trusting startup logs instead of querying live route state
- counting repeated `approval_pending` rewrites as progress
- trying to clear all instrumentation warnings before proving user-visible value

## Artifacts to update
When finishing this work, update the live status artifact:
- `docs/plans/2026-04-14-gsd-phase-ab-live-status.md`

Include:
- current phase
- what was added
- what was live-verified
- known warnings vs actual blockers
- next join point
