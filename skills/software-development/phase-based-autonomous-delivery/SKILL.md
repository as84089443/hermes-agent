---
name: phase-based-autonomous-delivery
description: Use for long-running buildouts where the user expects autonomous forward progress. Converts roadmap work into explicit phases, keeps one active phase in todo, treats maintenance interruptions as secondary, and always resumes the main line after verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planning, execution, autonomy, phases, delivery]
---

# Phase-Based Autonomous Delivery

## When to use

Use this when:
- the user wants you to keep pushing without repeated confirmation
- the work spans multiple architectural or implementation stages
- infrastructure interrupts (deploy logs, tunnel rotations, webhook churn, background process notices) may appear mid-stream
- the user explicitly cares that you do not stop after each small completion

Typical user signals:
- "直接做下一段"
- "主動推進"
- "不要每次都停下來問"
- frustration that you reported progress instead of continuing

## Core principle

Do not run the project as a loose list of next steps.
Run it as an explicit phase ladder.

Every non-trivial workstream should have:
- a named phase list
- exactly one active phase
- verification for each phase
- an automatic handoff to the next phase after completion

## Required workflow

### 1. Create a phase list before deep execution

For multi-step work, write a phase list into todo and/or a plan file.

Important planning-vs-execution rule:
- If the user asks for a roadmap or next phases during an already-active autonomous buildout, do NOT treat that as permission to stop at planning.
- Write the roadmap artifact, update todo/live status, then immediately resume the active implementation phase unless the user explicitly says they want planning only.
- In other words: roadmap writing is often a support action inside execution, not a reason to pause execution.

Each phase must define:
- Goal
- Deliverables
- Verification
- Done when
- Next phase

Example structure:

```markdown
### Phase 4 — Publish + closeout loop
Goal:
Connect publish-pack, final QA, closeout approval, and retro artifact generation.

Deliverables:
- closeout gate
- retro artifact generation
- human-readable approval text

Verification:
- typecheck/build pass
- publish-pack triggers final_qa
- final_qa triggers publish_closeout
- publish_closeout creates retro

Done when:
- project can complete end-to-end through closeout

Next phase:
- retro -> memory capture
```

### 2. Keep one active phase in todo

Use todo as the live execution pointer.

Rules:
- exactly one phase `in_progress`
- future phases `pending`
- completed phases marked immediately
- if a phase expands, split it but preserve the active-phase pointer

### 3. Finish the phase, then either:

A. begin the next phase immediately
or
B. run verification / regression / error checks first, then begin the next phase

Never stop at a status summary alone unless there is a real blocker.

### 3.1 Post-phase continuation rule
After finishing a phase, do not stop at "recommendations" if the next worthwhile improvement is already obvious and low-risk.

Required behavior:
- first decide whether the suggested follow-up is genuinely valuable
- if yes, start or complete that follow-up immediately
- if no, explicitly say why it is not worth doing yet

Do NOT:
- stop after giving advice the agent could have executed itself
- make cosmetic or low-value changes just to appear active
- keep changing things after the user-visible value has flattened

Good standard:
- continue when the next step increases clarity, usability, reliability, verification quality, or decision quality
- stop only when the next change would be speculative, redundant, or likely to create churn without meaningful gain

### 3.2 Marginal value check at phase boundaries
A common failure mode is local optimization: the phase is already useful, but the agent keeps polishing the same area because the next micro-improvement is easy to see.

Required check before staying in the same phase:
- has this phase already crossed the "usable threshold"?
- is the next change still high leverage, or just cleaner/safer/nicer?
- is another queued phase now the higher-leverage bottleneck?

If the phase is already usable and the next queued phase matters more, promote the current phase to complete and move on.
Do not let an easy-to-imagine local improvement trap the roadmap in the same phase.
### 3.5 Visible delivery rule

When the user expects autonomous momentum, hidden internal progress is not enough.
After each phase, produce at least one visible artifact the user can inspect immediately, such as:
- a wiki page
- a plan file
- a working UI change
- a generated route/output file
- a concrete checklist or spec page

And in the reply, point directly to the artifact path(s) and summarize exactly what changed.

If you say you are already moving to the next phase, you should still show the completed phase's tangible output first.

### 3.6 Live progress visibility

If the user wants to see ongoing motion instead of only milestone summaries, maintain a visible status artifact during execution.

Important distinction:
- a repo/wiki status artifact is necessary
- but for some users it is not sufficient
- if the user explicitly asks to keep seeing progress while work is underway, also send short in-chat progress updates after each meaningful subphase or blocker-resolution step

Good pattern:
- do a real chunk of work
- update the status artifact
- send a concise progress report with:
  - 目前主 phase
  - 剛完成什麼
  - 現在阻塞
  - 下一個 join point
- then continue working

Do not wait until a long batch is fully finished if the user explicitly asked for ongoing visible progress.

### 3.6.1 Mid-phase heartbeat rule

A visible status file alone is not always enough.
If the user explicitly says they want continuous progress reporting while work is underway, you must also send short in-chat heartbeat updates during execution.

Required behavior:
- after each meaningful slice lands, send a brief progress report instead of waiting for the whole round to finish
- if a maintenance event changes reality (for example dev server lock cleared, verification environment restored, tunnel rotated), report that immediately
- keep these updates compact and structured, not essay-like
- continue executing after the update; do not treat the update as a stopping point

Recommended heartbeat shape:
- 目前主 phase
- 剛完成什麼
- 現在阻塞
- 下一個 join point

Use this especially when:
- the user says they cannot see progress
- the work is long-running and verification takes time
- there are environment or process changes worth surfacing immediately

Important distinction learned from use:
- updating only the artifact is not enough when the user explicitly expects ongoing progress reports in chat
- if you are actively working across multiple tool turns, send short in-band progress updates at meaningful boundaries, not just a final wrap-up
- good cadence:
  - after locking the active phase
  - after a material implementation chunk lands
  - after verification completes
- each update should be compact and structured:
  - 目前主 phase
  - 剛完成什麼
  - 現在阻塞
  - 下一個 join point
- do not wait until the entire long phase is done if the user explicitly asked to see continuous progress while you work

Recommended pattern:
- create or update a lightweight status page (for example a wiki page like `live-execution-status.md`)
- include:
  - current active phase
  - phases just completed
  - what you are doing right now
  - what is queued next
  - any interrupt currently being handled
- when a maintenance interrupt happens (webhook rotation, tunnel URL churn, dev server noise), update the status artifact briefly, handle the interrupt, then return the status artifact to the main phase

This prevents the interaction from feeling like one command → one action while still giving the user something concrete to inspect between larger milestones.

### 3.6.2 Background automation visibility rule

When a phase introduces background automation (driver, scheduler, polling loop, timer-based worker), do not stop at "it should run now".
You must make the automation inspectable and prove that it is actually running.

Required pattern:
- expose a visible status surface such as a route, command, or artifact showing:
  - started/stopped state
  - last cycle time
  - last cycle reason
  - summary counts (scanned / attempted / transitioned / errored)
- verify both:
  - manual trigger works
  - automatic interval-based trigger works without manual intervention
- if possible, wait through at least one real interval and confirm `lastCycleAt` advances on its own

Also add a false-progress guard:
- background loops must distinguish real transitions from no-ops
- if the system is already waiting on the same human gate / blocker, return a noop result instead of rewriting identical state
- otherwise dashboards, summaries, and event logs will over-report progress and mislead operators

Good examples:
- status route returns `started: true`, interval ms, last cycle summary
- repeated run on an already-normalized approval state returns `noop_already_waiting_on_human_approval`
- live verification proves both startup cycle and later interval cycles happened

### 3.7 Multi-lane commander reporting

If the work is being run as a commander across multiple lanes, do not give freeform progress blurbs.
Use a fixed lane report shape every time.

Minimum reply sections:
- 目前主 phase
- 各 lane 狀態
- 現在阻塞
- 下一個 join point

Recommended lane model:
- spec gate
- plan gate
- execution lane
- review lane
- verification lane

Recommended lane statuses:
- not_started
- in_progress
- waiting_on_inputs
- blocked
- ready_for_review
- needs_revision
- passed
- frozen
- superseded

Also maintain a visible artifact in the repo or wiki with:
- current main phase
- lane-by-lane status
- known blockers
- next join point
- explicit out-of-scope note if later phases must not be mixed into the current round

If required input documents are missing, do not hallucinate them.
Mark them as input risks in the status artifact, continue with the available sources, and keep the main phase moving.

### 4. Treat maintenance events as interrupts, not new goals

Examples:
- localhost.run URL rotation
- Telegram webhook reset needed
- background process notices
- dev server restarts
- transient deployment logs

Handling rule:
1. fix the interrupt quickly
2. verify the interrupted service is healthy
3. immediately resume the active phase from todo
4. do not let the interrupt replace the roadmap

Concrete localhost.run pattern:
- if a new tunnel URL appears for a known service, treat it as a replacement for the prior temporary URL, not a new milestone
- verify the service immediately with a lightweight check before replying
  - dashboard or direct page: `curl -s -o /tmp/check.html -w '%{http_code}\n' <url>`
  - frontend that may redirect: `curl -L -s -o /tmp/check.html -w '%{http_code}\n' <url>`
- update the visible status artifact with the newest URL and explicitly say it replaced the previous temporary URL
- keep the response short: new URL, verification result, confirmation that work has resumed on the active phase

This is critical for tunnel/webhook-based workflows where high-frequency operational noise can derail strategic delivery.

### 5. After each phase, update the durable artifacts

Depending on scope, update one or more of:
- docs/plans/
- wiki pages
- relevant skills
- todo state

The project record should show where execution now stands.

## Good controller behavior

- "Phase 5 is now complete, verification passed, I have already started Phase 6."
- "Webhook rotated; I updated it and resumed the current donor-integration phase."
- "I finished the closeout loop, verified it, and moved directly into the retro-memory staging phase."

## Bad controller behavior

- finishing a phase and waiting for the user to say "continue"
- treating every operational interrupt as a new primary task
- reporting progress without verification
- keeping multiple roadmap phases in progress at once
- losing the main line because of background process chatter
- switching into answer-only mode when the user asks a meta question like "都完成了？" or "為什麼停住？" and failing to resume execution in the same turn

## Meta-question trap (root cause to avoid)
A recurring failure mode is:
1. user asks about completion, why progress stopped, or what remains
2. the agent answers correctly
3. but the answer itself becomes a stopping point
4. the main execution loop is not resumed immediately

Required fix:
- treat meta questions as an interruption report, not a new terminal state
- answer briefly, then in the same turn either:
  - resume the active phase with tool calls, or
  - explicitly explain the real blocker if execution cannot continue
- never end with a sentence like "next I should..." unless the corresponding work has already started in the same turn

## Reusable heuristics

### If the user prefers autonomous execution
Bias toward:
- fewer check-ins
- more done-before-reporting
- visible phase boundaries
- verification before summary

### If the work involves unstable tunnels/webhooks
Bias toward:
- short maintenance handling
- immediate resume of roadmap work
- explicit todo state so focus is not lost

### If the work involves architecture + implementation
Bias toward:
- plan file + todo phase pointer
- phase completion criteria
- rolling forward after each verified milestone

## Minimal checklist before replying

- Did I complete the active phase or move it forward materially?
- Did I verify the result?
- If an interrupt occurred, did I resume the main work afterward?
- Did I mark the next phase active instead of stopping at a report?
- Did I also capture or improve the method for pushing similar work forward next time (wiki, skill patch, script, config, or reusable contract)?

## Self-research requirement
For repeated project patterns, do not just complete the current task.
Also proactively research and develop a better method for advancing similar work in future.

Examples:
- If tunnel/webhook churn keeps interrupting progress, create an interrupt-handling rule and resume discipline.
- If review quality is inconsistent, define clearer review personas or verification rubrics.
- If the user repeats the same steering request multiple times, convert it into a durable operating method.

The goal is not only to finish tasks.
The goal is to become better at moving this user's projects forward over time.

## Remember

The user is not asking for passive progress updates.
They are asking for sustained autonomous momentum.

Your job is not only to do the work.
Your job is to keep the work moving.