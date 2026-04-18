---
name: hermes-daily-self-evolution-review
description: Run Hermes's daily self-evolution review against the wiki, recent sessions, and candidate queue; accept only low-risk learnings and sync status/index/log.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [self-evolution, wiki, review, cron, governance, verification]
    category: note-taking
---

# Hermes Daily Self-Evolution Review

Use this when Hermes is asked to run the recurring daily self-evolution review and directly update the wiki.

## When to use
- A cron job asks for the daily self-evolution review
- The task says to inspect recent sessions and update self-evolution status/queue pages
- You need to accept only low-risk, high-confidence learnings and defer the rest

## Goal
Turn the last day of high-signal work into a small number of evidence-backed learnings, update the self-evolution control pages, and avoid over-canonicalizing from weak evidence.

## Required evidence inputs
Read these first:
- `SCHEMA.md`
- `index.md`
- `log.md` (at least the recent section)
- `concepts/hermes-self-evolution-method.md`
- `operations/hermes-self-evolution-status.md`
- `operations/hermes-self-evolution-candidate-queue.md`

Then inspect recent sessions with `session_search()`:
- start with recent sessions
- follow with one or more focused keyword searches for self-evolution, candidate queue, repo-grounded research, skills/operator-guide work, and any live verification/control-surface tasks from the last day

## Daily review procedure
1. **Assemble evidence**
   - Pull the last 1 day or the most recent high-signal sessions
   - Prefer sessions that include real delivery, verification, failure, or routing corrections
   - Ignore low-signal chatter

2. **Distill the evidence**
   Extract exactly:
   - 1-3 most important learnings
   - 1-2 repeated failures or friction points
   - 1 one-shot success case

3. **Map each learning to a layer**
   Use one of:
   - `memory`
   - `skill`
   - `wiki`
   - `runtime`
   - `verification`
   - `governance`

4. **Apply the daily governance rule**
   - Only canonicalize low-risk, high-confidence changes
   - If evidence is thin, add or update a candidate in the queue instead of promoting it
   - Do not rewrite the self-evolution skeleton on the daily loop
   - Do not turn a single case into a global rule unless blast radius is low

5. **Update canonical artifacts**
   Always update `operations/hermes-self-evolution-status.md`:
   - `Latest accepted learnings`
   - `Current queue`
   - `Latest rejected/deferred changes`
   - `Next weekly review should ask`
   - `Last reviewed at`

   Update `operations/hermes-self-evolution-candidate-queue.md` when:
   - evidence strengthens an existing candidate
   - a new accepted low-risk rule appears
   - a provisional idea must be explicitly deferred

   If a low-risk rule is accepted, add it to the relevant canonical page too (often `hermes-self-evolution-method.md`).

6. **Sync the wiki spine**
   If any wiki page changed, also update:
   - `index.md` last-updated marker
   - `log.md` with a dated review entry

7. **Verify**
   Re-read the edited files and confirm:
   - status, queue, method, index, and log agree with each other
   - accepted/deferred decisions are visible
   - no evidence-poor item was silently canonicalized

## Strong pattern learned
For live UI or control-surface checks, visual evidence alone is not enough when the page delta is weak. Prefer:
- browser interaction proof
- plus API / event / artifact proof

This belongs in the `verification` layer and is safe to accept on the daily loop when backed by multiple live cases.

## Output format
Report:
- reviewed evidence
- updated artifacts
- accepted decisions
- deferred decisions
- rejected decisions
- items that need weekly handling

## Pitfalls
- Do not treat the daily review as a place to redesign the whole self-evolution framework
- Do not canonicalize broad runtime rules from a narrow cluster of task types
- Do not update wiki pages without syncing `index.md` and `log.md`
- Do not stop at a reflective summary; make the safe wiki updates directly
