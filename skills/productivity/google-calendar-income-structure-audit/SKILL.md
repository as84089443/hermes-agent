---
name: google-calendar-income-structure-audit
description: Audit a user's messy Google Calendar plus Google Sheets income ledger by iteratively confirming classification rules before drawing business conclusions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [google-calendar, google-sheets, income-analysis, data-cleaning, decision-support]
---

# Google Calendar + Income Structure Audit

Use this when:
- A user wants business/life pattern analysis from messy Google Calendar history
- The user also has a Google Sheets income or compensation ledger
- Calendar entries mix personal, family, partner, BNI/community, passive-income, and work events
- The data quality is messy enough that direct analysis would likely be wrong

## Goal
Build a decision-useful model from noisy Google data without overcommitting to false classifications.

## Core principle
Do NOT jump straight to final insights. First build trust in the classification logic with the user.

The correct sequence is:
1. connect data sources
2. export history
3. build provisional layers
4. ask the user to correct the layer rules
5. separate high-confidence from needs-review
6. only then produce business conclusions

## Data sources
- Google Calendar history export (all accessible calendars, past events)
- Google Sheets income ledger (often annual sheets like `2025年公司酬勞表`)

## Workflow

### 1. Connect Google Workspace
Use the `google-workspace` skill first.
Important experiential finding:
- `setup.py` may fail to import `hermes_constants` unless run with `PYTHONPATH` pointing at the hermes-agent repo root.
- Pattern:

```bash
source venv/bin/activate
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="$(pwd)/venv/bin/python"
PYTHONPATH="$(pwd)" "$PYTHON_BIN" "$GWORKSPACE_SKILL_DIR/scripts/setup.py" --check
```

### 2. Export complete calendar history
Do not rely on 7-day agenda helpers for this task.
Use the Calendar API directly to fetch:
- all calendars from `calendarList`
- all past events up to `now`
- `singleEvents=True`
- large pagination (`maxResults=2500` + `nextPageToken` loop)

Store a raw export JSON under a stable profile-scoped export path, e.g.:
- `~/.hermes/exports/google_calendar_history/calendar_history_<timestamp>.json`

For each event, preserve at least:
- calendar summary/id
- title/summary
- start/end
- location
- attendees
- organizer/creator
- recurringEventId
- eventType

### 3. Build provisional analysis layers
Start with coarse layers, not final truth. A useful initial set:
- `personal_core`
- `shared_work`
- `passive_income`
- `secondary_context`
- `isolated_reference`
- `unknown_review`

Examples of useful user-correctable rules discovered in practice:
- A shared chapter/community calendar may contain one highly relevant recurring event and lots of irrelevant noise.
- Partner/family calendars may be visible only for availability awareness and should be isolated from the user's own rhythm.
- A studio calendar may mix direct operations with rental bookings; `租棚` should often become passive-income instead of direct workload.
- A shared work calendar may represent collaboration with a partner, not solo work.

Store a machine-readable rules file, e.g.:
- `calendar_relevance_rules_<date>.json`

### 4. Ask the user to correct the logic before deep analysis
This is the key reusable lesson.
If the user says their data is messy, STOP broad inference and switch to confirmation mode.

Use short clarification rounds to confirm:
- which calendars are truly theirs vs only reference calendars
- which recurring events are actually relevant
- whether spouse/partner calendars should be low-confidence or isolated
- whether calendar events represent direct work, PM/BD, support, or passive income
- how to interpret income splits (e.g. Brian vs Chu vs Jerry)

Best practice:
- ask one boundary question at a time
- offer numbered choices (1/2/3/4) when the user is choosing a framework
- when reviewing messy historical rows, switch to very small batches (5 items worked well in practice)
- accept partial answers; if the user only remembers client ownership or one role dimension, record that and leave the remaining fields pending instead of forcing a full structured answer
- after each answer, restate the updated rule clearly

### 5. Refine unknowns before making conclusions
Break `unknown_review` into smaller buckets such as:
- `public_holiday_background`
- `possible_work_support`
- `misc_background`

This improves explainability and prevents background holidays from polluting business conclusions.

### 6. Separate business analysis from life-rhythm analysis
Do NOT force one mixed model.
Create at least two future analysis tracks:
- life-rhythm / personal operating rhythm
- business / owner-decision analysis

If the user wants business-first, then further confirm the business logic.

### 7. For income analysis, classify by economic role, not just event count
When ingesting annual compensation sheets, normalize these ideas separately:
- Brian personal income pool: any row where Brian receives a split
- core execution income: Brian personally worked and was primary output
- PM/BD income: Brian took the job / managed delivery / was the accountable owner even if not the main on-site executor
- collaboration/support income: Brian was present but in assistant/support mode
- passive income: rental/asset line, separate from active labor
- spouse unit: keep Brian, Chu, and combined spouse unit views simultaneously when relevant

Important experiential finding:
- Do NOT assume shared splits imply PM/BD.
- Do NOT assume calendar event counts equal work effort or income weight.
- Empty rows / monthly subtotal rows / aggregate rows in Sheets must be filtered before classification.
- Keep `needs_review` as a first-class category for ambiguous rows.

### 8. Confidence-split the income model
A reusable pattern that worked well:
- `core_execution_high`
- `core_execution_medium`
- `pm_bd_high`
- `pm_bd_medium`
- `collab_support_high`
- `needs_review`

This prevents overclaiming from weak heuristics.

### 9. Only then present owner-level conclusions
Safe conclusions usually come from:
- trends that survive confidence filtering
- user-confirmed calendar semantics
- income rows with explicit role cues

State clearly:
- what is high-confidence
- what is directionally likely but not final
- what still requires user confirmation

## Practical heuristics learned

### Calendar heuristics
- `租棚` inside a studio calendar is often passive income, not direct workload.
- Family/reference calendars should be isolated if the user only watches them for availability.
- Shared work calendars should become `shared_work`, not `personal_core`.
- Community/network calendars (e.g. BNI) often need partial relevance rules, not full inclusion or exclusion.

### Income heuristics
- If the user says “only if I have a split, count it in my income pool”, follow that.
- If the user says “if I’m not the main output, treat it as PM/接案”, prioritize economic role over presence.
- If spouse post-production exists, keep three views:
  - Brian alone
  - Chu contribution
  - Brian+Chu unit
- Client ownership is often upstream of all other role logic. If a client is explicitly the user's client, the row may simultaneously count as PM/BD and core execution rather than forcing a single label.
- When Brian and Jerry net amounts are very close, that is a useful heuristic for `shared client / shared PM`, but treat it as medium-confidence until the user confirms.
- If the user says “if the client is mine, I basically count as PM”, treat client ownership as a strong PM signal unless contradicted.
- Do not force every reviewed row into a fully specified schema. A partial confirmation like “this is my client” is still valuable; update only that field and preserve the rest as pending.

### Shared-sheet rule learned in practice
If the source Google Sheet is collaboratively used by multiple people, do NOT pollute the shared operational sheet with Hermes-only analysis columns.
Instead:
- keep the shared Google Sheet unchanged
- export it locally
- build a profile-scoped `sidecar` customer master / rule file under `~/.hermes/exports/...`
- store inferred fields there, such as:
  - `client_owner_guess`
  - `pm_owner_guess`
  - `relationship_type_guess`
  - `confidence`
  - `notes`
- if the business also uses sub-brands (for example a wedding sub-brand separate from the legal vendor), create a second local `brand sidecar` rather than forcing those semantics into the shared vendor sheet
- merge the sidecar(s) back into the local normalized income dataset, not the original collaborative sheet

This preserves shared workflow hygiene while still letting Hermes accumulate reusable business-logic knowledge.

### Important convergence lesson: prefer the explicit vendor column over case-title guessing
If the income sheet has a dedicated vendor/customer column, treat that as a stronger signal than the case title.

Practical order of trust:
1. explicit vendor column in the sheet
2. vendor sidecar / brand sidecar match
3. user-confirmed rule or conversation note
4. case-title heuristic

Why this matters:
- case titles are noisy and role-heavy
- the vendor column often reflects the business entity or client line more reliably
- many "low-confidence" rows are not truly role-ambiguous; they are customer-unmatched

Reusable workflow:
1. read the annual compensation sheet including the vendor column, not just date/title/splits
2. build a `(sheet, date, case) -> vendor_raw` lookup
3. normalize vendor aliases (e.g. abbreviated names vs legal names, sub-brands vs legal entity)
4. merge the vendor match into the normalized historical income table
5. only after vendor matching, revisit remaining low-confidence rows

Expected result:
- fewer rows in `待確認`
- better client-owner / PM-owner guesses
- faster convergence when reviewing old data with the user

### Important convergence lesson: customer ownership is often the best next question
When the user struggles to remember full role breakdowns, do not force a full schema answer. Often the fastest convergence path is:
1. ask only who the client belongs to (`mine / Jerry / shared / upstream / don't remember`)
2. if the user says the client is theirs, treat that as a strong PM signal by default
3. only ask PM/execution follow-ups when customer ownership alone does not resolve enough ambiguity

This is especially effective when the user says things like:
- "if the client is mine, I basically count as PM"
- "if Brian and Jerry amounts are close, it's usually a shared client and not a designated single PM"

### Important convergence lesson: low-confidence rows usually need customer mapping first
When many low-confidence income rows remain, do NOT immediately keep asking about PM/execution role row by row.
First check whether the bottleneck is actually missing customer alignment.

A reusable pattern that worked well:
1. cluster low-confidence rows by matched vendor / keyword family
2. identify whether most ambiguity comes from `unmatched customer` rather than `unclear role`
3. ask the user only for customer identity or customer type on the highest-value unknown rows
4. update the vendor sidecar first
5. only then resume PM/execution review

This often reduces uncertainty faster than asking full role questions too early.

### Clarification ergonomics learned in practice
For messy historical rows:
- start with the narrowest missing dimension
- if the user only remembers customer ownership, accept that and stop there
- do not insist on getting client owner + PM owner + execution in one turn
- once a pattern becomes clear (e.g. "if the client is mine, I basically count as PM"), promote it into a global heuristic and apply it going forward

This keeps the review lightweight and avoids user fatigue while still improving the model.

## Pitfalls
- Over-reading titles before user clarification
- Treating a visible family/partner calendar as the user's own workload
- Treating event count as value density
- Treating PM/BD, execution, support, and passive income as one bucket
- Making final business claims before `needs_review` is acknowledged
- Forgetting to filter subtotal/blank rows in income sheets

## Good output artifacts
- raw calendar export JSON
- calendar relevance rules JSON
- layered cleaned calendar dataset
- calendar structure diagnosis by year
- calendar + income cross-diagnosis JSON
- confidence-split Brian business decision dataset

## Done when
- the user has confirmed the key semantic boundaries
- calendar layers reflect real ownership/relevance
- income rows are split into high-confidence buckets plus `needs_review`
- conclusions are framed with explicit confidence levels
- the user can actually use the result for owner decisions, not just descriptive stats
