---
name: hermes-wiki-bootstrap
description: "Bootstrap and expand a Hermes LLM Wiki: schema, index, seed pages, skills catalog, Obsidian integration, sync, and verification."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, bootstrap, obsidian, sync, skills, configuration, troubleshooting]
    category: note-taking
---

# Hermes Wiki Bootstrap

Use this skill when the user wants to create or expand an LLM Wiki on a Hermes installation, especially when the wiki should become the durable knowledge graph for skills, configuration, memory, profiles, and troubleshooting.

## When to use
- User asks to "build a wiki" for Hermes or another agent setup
- User wants skills turned into searchable knowledge pages
- User wants Obsidian to open the same vault Hermes uses
- User wants a one-shot, end-to-end setup with minimal back-and-forth

## Goal
Create a practical wiki that compiles Hermes knowledge into linked markdown pages with a clear schema, an index, a log, and core operational pages.

## Procedure

### 1) Inspect the active Hermes profile
- Resolve `HERMES_HOME` and the active config path.
- Check existing `config.yaml`, `.env`, skills directory, and any existing wiki path.
- Identify whether the user is already using a profile-isolated setup.

### 2) Establish the wiki root
- Default to `~/wiki` unless the active config says otherwise.
- Create or verify:
  - `SCHEMA.md`
  - `index.md`
  - `log.md`
  - `raw/`
  - `concepts/`
  - `comparisons/`
  - `queries/`
- If sources are being ingested, store them under `raw/` and keep them immutable.

### 3) Seed the core knowledge graph
Create or update the foundational pages first:
- `start-here`
- `hermes-agent`
- `configuration`
- `skills`
- `skills-catalog`
- `skills-ecosystem`
- `skills-sync`
- `memory`
- `profiles`
- `wiki-architecture`
- `troubleshooting`
- `skills-vs-memory`
- `roadmap`
- `wiki-maintenance`
- `model-provider-routing`
- `session-recall`
- `obsidian-vault`
- `sync-between-computers`

When the skills inventory is large, do not stop at a flat catalog: add a top-level family page and then split it into capability subpages so the wiki becomes a navigable graph instead of a single long list.

### 4) Generate a skills catalog
- Enumerate installed skills under `~/.hermes/skills/`.
- Group them by category path.
- Write a summary page that lists each skill with a one-line description.
- Link the catalog back to `skills`, `skills-sync`, and `configuration`.

### 5) Connect Obsidian
- Set `OBSIDIAN_VAULT_PATH` to the wiki directory when the user wants the same markdown vault visible in Obsidian.
- Make sure the wiki pages use standard markdown and wikilinks so Obsidian renders them naturally.

### 6) Sync the environment
If the user wants multi-machine parity, sync these items:
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/skills/`
- `~/wiki/`

Prefer git for the wiki and skills when possible; use rsync/scp for one-off copies.

### 7) Verify the result
Before finishing, verify:
- The wiki index lists every created page.
- The log records the bootstrap/expansion actions.
- Wikilinks resolve to real pages.
- The config contains the wiki path.
- The Obsidian vault path is set when requested.
- The skills catalog matches the installed skills.

## Practical lessons learned
- For broad wiki bootstrap tasks, direct synthesis plus structured file generation is more reliable than spawning broad subagent research; large context jobs can burn through iterations without producing a useful output.
- Use code to enumerate installed skills and generate the catalog from the real local inventory; do not hand-curate a large skills list from memory.
- Build the wiki in phases and update the index after each phase so the navigation stays coherent.
- Avoid wikilinks to non-content files like `index.md` and `log.md`; use plain text references for those.
- If the wiki is meant to double as an Obsidian vault, keep the vault path and Hermes wiki path identical unless there is a specific reason not to.
- Add an explicit `control-center` page once the wiki grows beyond a seed set; use it as the practical front door for live status, transfer routes, and operating policy.
- Add an `autonomous-execution-policy` page when the user wants the agent to keep moving without constant confirmation; link it into `start-here`, `blueprint`, `troubleshooting`, and the topic map.
- When importing another machine's transfer bundle, preserve three layers separately: raw archive record, full provenance graph, and compact daily-use operating panel.
- If a research report contains a future-state vision (for example, turning Hermes into an AI video department), extract that vision into a dedicated wiki page and cross-link it into the control center and roadmap so it becomes part of the operating model.
- After large wiki edits, run a link-validation pass and also check for orphan pages and stale index counts; repair the index/log immediately if the validation reveals drift.

- If autonomy is part of the workflow, document it in the wiki as a policy page and link it from the index/topic map so the behavior is discoverable.
- Avoid wikilinks to non-content files like `index.md` and `log.md`; use plain text references for those.
- If the wiki is meant to double as an Obsidian vault, keep the vault path and Hermes wiki path identical unless there is a specific reason not to.

## Validation lessons
- Regex-based wikilink validation can misclassify literal mentions like `[[wikilinks]]` inside prose or examples. Strip code spans / literal examples or exempt documentation text before counting broken links.
- After a large expansion, verify the graph, then update the page count in the index and log together so metadata stays consistent.
- Keep raw transfer/source capture pages linked into the index so recovered archives do not become orphans.

## Pitfalls
- Do not hardcode `~/.hermes` in wiki content or code paths when profile-aware helpers exist.
- Do not modify raw source captures in `raw/` after saving them.
- Do not create disconnected pages without cross-links.
- Do not skip the index or log; they are the backbone of the wiki.
- Do not assume the same home directory or profile is active across machines.
- If file protection blocks direct writes to credential files, fall back to a terminal-based edit only when appropriate and safe.
- Do not trust naive link validators that treat literal `[[...]]` prose as actual links.
- Do not enforce a strict “2 outbound links” rule on every page; exempt raw/leaf pages when a hub page carries the graph structure.

## Verification checklist
- [ ] `SCHEMA.md` exists and matches the domain
- [ ] `index.md` includes all created pages
- [ ] `log.md` records each phase
- [ ] Core pages link to each other
- [ ] Skills catalog is complete and grouped
- [ ] Obsidian points at the same vault path
- [ ] Sync guidance is documented
- [ ] Control-center and autonomy policy pages exist
- [ ] Raw transfer/source capture pages are indexed and not orphaned

## Output style
When executing this skill, prefer a concise plan, then complete the work in one pass. Report the created/updated files and any verification results at the end.