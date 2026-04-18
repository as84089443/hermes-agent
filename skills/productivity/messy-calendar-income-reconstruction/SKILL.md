---
name: messy-calendar-income-reconstruction
description: Reconstruct a usable business map from messy Google Calendar + Google Sheets income records by building local sidecars, iteratively confirming role logic with the user, and avoiding edits to shared source sheets.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [calendar, google-sheets, business-analysis, data-cleaning, sidecar, income-mapping]
---

# Messy calendar + income reconstruction

Use when:
- The user has messy Google Calendar and/or Google Sheets business records
- Multiple people are mixed together in one system (spouse, partner, family, collaborators)
- Shared sheets must NOT be polluted with analyst-only columns
- The goal is to derive a decision-quality business map, not just dump raw data

## Core principles

1. Do NOT trust raw labels at face value.
2. Separate user-confirmed facts from heuristic guesses.
3. Keep shared source sheets pristine; put analyst-only structure in local sidecars.
4. When the data is messy, switch from bulk analysis to small-batch user confirmation.
5. Prefer customer ownership over naive split-ratio logic.

## Recommended workflow

### 1. Build the raw exports first
- Export full historical calendar data to a local JSON file.
- Export the relevant Sheets tabs (income tables, vendor master, etc.) to local normalized files.
- Keep immutable raw snapshots before adding interpretation.

Suggested outputs:
- `calendar_history_<timestamp>.json`
- `historical_income_normalized_v1_<date>.json`

### 2. Ask for exclusion / relevance rules early
Before serious analysis, ask who/what should be excluded or downgraded.
Examples that proved critical:
- Some calendars are only visibility calendars for partners/family, not part of the user’s own life/work analysis.
- Some shared calendars contain lots of irrelevant chapter/org noise.
- Passive-income events (e.g. studio rental) should be separated from active work.

Store these as local rules and, if durable, in memory.

### 3. Split calendar analysis into layers
A useful layer model:
- `personal_core`
- `shared_work`
- `passive_income`
- `secondary_context`
- `isolated_reference`
- `public_holiday_background`
- `possible_work_support`

Important learned rule:
Do not force one blended "truth" from mixed calendars. Keep isolated and second-layer data visible but separate.

### 4. Do NOT write analyst columns into shared sheets
If the vendor/customer sheet is shared by multiple humans, create a local sidecar instead.

Use local sidecars like:
- `vendor_master_sidecar_v1_<date>.json`
- `customer_brand_sidecar_v1_<date>.json`
- `brian_review_rules_notes_<date>.json`

These should contain fields such as:
- `client_owner_guess`
- `pm_owner_guess`
- `relationship_type_guess`
- `confidence`
- `notes`

### 5. Treat customer ownership as a first-class signal
A major learned correction:
- Split ratios and attendance are not enough.
- If the client is the user’s client, the job can still count as the user’s PM/BD income even if execution was delegated.
- In messy real-world records, a good default is: client owner usually implies PM owner unless the user says otherwise.
- Some jobs are both PM/BD and core execution.
- If user and partner income are close, that often indicates a shared client / shared PM pattern rather than a single owner.
- Relationship context matters: BNI partners, ex-colleagues, wedding sub-brands, and upstream agencies can be stronger signals than the job title itself.

### 6. Use role logic, not only category logic
Do not force each job into one exclusive bucket too early.
A better role set:
- customer owner
- PM/BD owner
- user executed?
- user role = main output / support / management / not involved
- asset income?

For messy history, maintain both:
- a simplified classification field for rollups
- the underlying role fields for future reclassification

### 7. Confirm in tiny batches
When user memory is partial, ask in batches of 5 max.
This worked much better than asking 15+ rows at once.

Two effective question modes:

A. Single-axis customer matching
Ask only:
- my client / partner’s client / shared client / upstream / don’t remember

B. Three-question role confirmation
Ask only:
- client owner?
- PM owner?
- did the user personally execute?

Do NOT insist on all fields if the user only remembers one dimension. Record partial truth and leave the rest pending.

### 8. Rebuild normalized tables after each meaningful rule update
After gaining new rules, regenerate the normalized output rather than keeping stale earlier logic.
Version outputs clearly:
- `historical_income_normalized_v2_...`
- `historical_income_normalized_v3_...`
- etc.

Track:
- confidence counts (high / medium / low)
- customer-owner counts
- PM-owner counts
- top unresolved clusters

### 9. Cluster low-confidence rows by system, not only by row
Useful cluster dimensions:
- brand system (e.g. wedding sub-brand)
- client system
- upstream partner
- org/community network (e.g. BNI)
- unmatched/no-vendor rows

This often reveals that the real bottleneck is not role uncertainty but missing customer mapping.

### 10. Prefer source columns over heuristics when available
A key experiential finding:
If the income sheet contains a dedicated vendor/customer column, use that as the primary anchor. Do not over-rely on project names if the vendor column exists.

Important follow-up learned in practice:
- The vendor/customer column may have been filled in only later, or only for some years/rows.
- Re-check the live sheet after the user says they started adding vendor prefixes/columns — do not assume your earlier snapshot still reflects the current state.
- Some highest-value unresolved rows will still have vendor=`-` or blank; those must be handled through sidecars and user memory, not forced inference.

Priority order:
1. Rulebook / do-not-ask-again cases
2. Vendor/customer column in source sheet
3. Local vendor sidecar / brand sidecar
4. User-confirmed notes
5. Name-based heuristics

Important operational refinement learned in practice:
- If the source sheet already has a dedicated vendor/customer column, do a fresh pass to backfill from that column BEFORE asking the user about more rows.
- Once a case or client line has been confirmed, add it to a do-not-ask-again ledger and suppress repeated prompts about the same mapping.
- If the remaining unresolved rows mostly have vendor=`-` or blank, switch the questioning strategy to customer-mapping-only mode instead of asking for full role classification.
### 11. Preserve partial truth and avoid repeat questioning
When the user answers only one part of a multi-field question:
- Save the confirmed dimension immediately (for example, customer ownership only)
- Leave PM/execution fields pending
- Do NOT keep re-asking the full structured question if the user already provided usable partial truth

Also maintain a lightweight "already confirmed" ledger for cases/brands so you do not ask about the same mapping repeatedly. This became important once the reconstruction spanned many batches.

### 12. Add a brand/relationship layer, not just vendors

Also maintain one consolidated local rulebook file that sits above raw exports and sidecars, for example:
- `analysis_rulebook_v1_<date>.json`

Use it to store:
- calendar exclusion/downgrade rules
- customer/brand ownership rules
- repeat-question suppression (`do_not_ask_again`)
- key exemplar cases that define the logic
- the exact priority order for future lookups

This rulebook should be checked BEFORE asking the user new questions.

A practical lookup order that worked better than ad-hoc reasoning:
1. Rulebook / do-not-ask-again cases
2. Vendor sidecar
3. Brand sidecar
4. Raw vendor/customer column in the source sheet
5. User clarification
6. Name-based heuristics as the last resort

### 13. Prefer progressive clarification over rigid forms

When the user is recalling old business history, do not insist on one rigid answer format forever.
Useful progression learned in practice:
- first ask single-label classification (e.g. core / PM / support)
- then switch to 3-question role logic (`client owner / PM owner / did the user execute?`)
- when that still causes friction, simplify further and ask ONLY for customer mapping

The right question is the smallest one that reduces uncertainty.

### 14. Reuse the user’s own language as rules

If the user says things like:
- “If it’s my client, I’m effectively PM”
- “If Brian and Jerry split is close, it’s usually a shared client”
- “This wedding line belongs to 麻花影像 and Chu usually controls it”

then convert those statements into explicit reusable rules immediately.
Do not leave them buried in transcript text.
Some business logic sits above individual vendors:
- wedding sub-brands
- BNI relationship lines
- upstream agencies
- specific people (e.g. partner, BNI member, ex-colleague) who consistently indicate client ownership

Create a local brand/relationship sidecar when needed, for example:
- `customer_brand_sidecar_v1_<date>.json`

This should capture reusable business context such as:
- shared-operated sub-brand
- who usually controls PM
- whether a relationship line is "my client," "shared," or "upstream"
- negative memory like "do not keep collaborating"

## Practical heuristics that worked well

- Wedding jobs with terms like `婚禮`, `早儀`, `午宴`, `抓周`, `SDE`, `VAF` can often be grouped under the wedding brand system first, then refined.
- Shared client / shared PM is a reasonable temporary heuristic when user and partner payouts are very close.
- If vendor column is `-`, expect more manual clarification.
- If a user says “this is my client, but I sent it to someone else to shoot,” classify as PM/BD income, not core execution.

## Outputs to maintain

1. Raw exports
2. Layered calendar file
3. Vendor sidecar
4. Brand sidecar
5. Review notes file
6. Versioned normalized income table
7. Low-confidence cluster map
8. Business map / decision map

## Pitfalls

- Do not turn partial memory into forced certainty.
- Do not mutate shared source sheets just to make analysis easier.
- Do not assume split ratio equals customer ownership.
- Do not merge passive income into active labor income.
- Do not ask giant confirmation batches; use 5-row batches.

## Done when

- The user agrees the classification logic matches real-world business logic
- Shared-source data remains untouched
- Most rows are high or medium confidence
- Remaining low-confidence rows are clustered into a few understandable systems
- You can explain the business using role-based panels rather than one blended total
