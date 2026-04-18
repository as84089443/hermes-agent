---
name: ai-department-browser-ui-smoke-qa
description: Run the browser-based UI smoke suite for Hermes dashboard + AI Department OS, generate screenshots/reports, and verify a real approval decision through the front-end.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qa, browser, smoke-test, playwright, ai-department-os, regression]
---

# AI Department Browser UI Smoke QA

Use when working on `/Users/brian/dev/ai-department-os` and you need a real browser regression artifact instead of API-only smoke.

## What this validates

This suite covers browser flows plus backend verification in a small matrix:
1. Hermes dashboard shell loads in a real browser
2. `/projects` shows the boss-mode overview sections
3. `/projects/[id]` shows the three decision summary cards
4. `/approvals` can submit `changes_requested` through the desktop UI
5. `/approvals` can submit `approved` through a mobile viewport UI flow
6. API re-check confirms each browser action actually changed project state, event payloads, and stored decision notes

## Canonical files

- `scripts/qa/run_browser_ui_smoke.py`
- `scripts/qa/run-browser-ui-smoke.sh`
- `scripts/qa/browser_ui_smoke.spec.js`
- `docs/qa/browser-ui-smoke-checklist.md`
- `docs/plans/2026-04-14-browser-ui-smoke-artifact.md`

## Report output

- `qa-output/browser-ui-smoke/<timestamp>/report.md`
- `qa-output/browser-ui-smoke/<timestamp>/report.json`
- `qa-output/browser-ui-smoke/<timestamp>/screenshots/`
- `qa-output/browser-ui-smoke/<timestamp>/playwright-report.json`
- `qa-output/browser-ui-smoke/<timestamp>/logs/playwright.log`

## How to run

From `/Users/brian/dev/ai-department-os`:

```bash
npm run qa:browser-ui-smoke -- --cleanup-created-project
```

Equivalent direct wrapper:

```bash
./scripts/qa/run-browser-ui-smoke.sh --cleanup-created-project
```

## Service behavior

The runner reuses or starts:
- Hermes dashboard at `http://127.0.0.1:9119`
- AI Department OS at `http://127.0.0.1:3010`
- if `3010` is unavailable but `3000` is already serving the app, it reuses `3000`

## Important implementation pattern

Do not start with a blank browser and hope useful data exists.

The runner first creates a dedicated smoke project via API, then Playwright navigates the real UI around that project. This makes the browser checks deterministic and allows the approval form flow to be verified end-to-end.

## What the Playwright spec asserts

### Dashboard
- page title matches `Hermes Agent`

### Projects page
- `Phase 表`
- `先看這些待拍板案子`

### Project detail page
- `目前方向`
- `目前階段`
- `目前卡點`

### Approvals page
- locate the desktop smoke card and submit `changes_requested`
- locate the mobile smoke card under a mobile viewport and submit `approved`
- verify the pending card disappears from `/approvals` after each submission

### Backend re-check after browser action
- desktop path:
  - project status becomes `revise`
  - approval status becomes `changes_requested`
  - `approval-prep` task becomes `needs_revision`
- mobile approved path:
  - project status becomes `in_progress`
  - approval status becomes `approved`
  - `approval-prep` task becomes `done`
- for both paths:
  - latest `approval_decided` event payload matches the submitted status
  - latest `approval_decided` event payload stores the submitted decision notes
  - approval record stores the submitted decision notes

## Known pitfalls

1. `@playwright/test` must be a real devDependency in this repo
- relying only on transient `npx playwright test` resolution caused module import failures from the spec file
- keep `@playwright/test` in `package.json`

2. `npx playwright install chromium` may print a warning if the dependency graph is not installed yet
- this is acceptable after `npm install`
- once `@playwright/test` exists and Chromium is present, the runner should proceed normally

3. Hermes dashboard home may not have stable visible body text
- the browser check should assert the page title `Hermes Agent`, not brittle homepage DOM copy

4. Boss-mode card labels can collide with nearby descriptive text
- for `目前方向 / 目前階段 / 目前卡點`, use exact text matching in Playwright to avoid strict-mode ambiguity

## Verification standard

A successful run means:
- runner exit code 0
- all four browser tests passed
- API verification passed after the browser form submission
- report + screenshots written under `qa-output/browser-ui-smoke/...`

## Good next upgrades

- add mobile viewport coverage
- add a second decision-path matrix for `approved`
- attach this browser smoke to demo-day or pre-closeout regression runs
