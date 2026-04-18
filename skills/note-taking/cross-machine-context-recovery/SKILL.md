---
name: cross-machine-context-recovery
description: Recover durable memory, skills, and continuity artifacts from a transfer bundle or archive created on another machine, then classify them into Hermes memory, Hermes skills, and wiki pages.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [recovery, transfer, memory, skills, wiki, archive, migration]
    category: note-taking
---

# Cross-Machine Context Recovery

Use this skill when the user gives you an archive, export folder, or transfer pack from another computer and wants you to recover their memory, skills, prompts, or continuity context.

Typical triggers:
- "這是我另一台電腦的資料，幫我拆解看看"
- "從這包裡把記憶和技能拿回來"
- "把另一台機器的 context 匯回 Hermes"
- "import transfer pack / archive / backup"

## Goal

Turn an unfamiliar transfer bundle into three useful outputs:
1. Durable Hermes memory entries for stable facts, preferences, decisions, and procedures
2. Reusable skills copied or adapted into `~/.hermes/skills/`
3. Wiki pages that preserve the recovered structure, sources, and migration notes

## Workflow

### 1) Inspect the bundle before importing anything

Start with a directory and manifest pass. Do not assume the archive contents are already loaded or safe to import.

Check for:
- top-level README or manifest files
- `memory/` exports
- `skills/` trees
- `rules/` or system prompt files
- `continuity/` handoff or workspace memory files
- `extra/` metadata, logs, or runbooks

Prefer a quick structural inventory first:
- list files and directories
- count skill trees and memory records
- identify obvious duplicates or mirrored skill layouts
- note whether the bundle is extracted or still compressed

### 2) Classify content by destination

Separate the archive into these buckets:

- `memory/` → durable facts, preferences, decisions, procedures, incidents
- `skills/` → reusable operating procedures or prompts
- `rules/` → policy or system guidance that may become prompt text or wiki notes
- `continuity/` → migration evidence, handoffs, workspace memory manifests
- `extra/` → auxiliary metadata, logs, or import runbooks

Do not write everything into memory. Only keep stable items.

### 3) Import memory conservatively

When writing to Hermes memory:
- keep entries compact and durable
- prefer stable facts, preferences, and procedures
- skip task state that is clearly temporary unless it matters long-term
- skip secrets, tokens, passwords, and personal sensitive data
- if a new memory conflicts with an older one, close or supersede the old fact instead of keeping both

A good rule is: if it would still matter a month later, it may belong in memory.

### 4) Recover skills carefully

For each skill tree in the bundle:
- inspect its `SKILL.md`
- read the `name:` and `description:`
- decide whether it is reusable in Hermes as-is, or whether it needs adaptation
- check for collisions with existing Hermes skills
- remove `.DS_Store` and AppleDouble `._*` files when copying trees
- preserve symlink structure when a copied tree depends on canonical relative links; some imported skill ecosystems use symlinked or mirrored layouts

If the bundle contains multiple skill ecosystems, keep them in a dedicated namespace or category folder first, then curate later.

### 4.1) Build a wiki skill graph, not just a flat list

When the transfer pack is large, create a top-level wiki page for the recovered family and then split it into subpages by capability cluster.

A good pattern is:
- one provenance/overview page for the whole transfer pack
- several second-level subpages for major capability families
- optional third-level pages for especially dense families
- a leaf-level page per skill when the source tree is large enough to warrant individual navigation targets

Keep the top-level page as the source-of-truth hub and use the subpages for navigation depth.

### 4.2) Create both a full map and a compact operating view

For large recovered ecosystems, do not stop at a single full inventory.

Produce three complementary layers:
- full map: exhaustive provenance + skill tree coverage
- core shortlist: a small reusable set of high-frequency, low-ambiguity skills
- operating panel: a Now / Next / Later view that turns the shortlist into an execution sequence

This avoids the common failure mode where a large recovered bundle is technically documented but not practically usable.

Useful heuristics for the shortlist:
- favor cross-project utilities over niche one-offs
- favor skills that reduce coordination friction, reviews, or handoff risk
- keep design/docs/PDF/media helpers if they are frequently reused
- keep continuity/checkpoint/backup skills if they protect work in progress

If the user specifically wants one-shot completion, include the compact operational view in the same pass rather than deferring it.

## 5) Create a wiki transfer record

Always leave a breadcrumb in the wiki.

Create a raw transfer note that records:
- source archive path
- extracted directory
- what kinds of artifacts were present
- what was imported vs deferred
- what still needs review

Also update the wiki index and log so the transfer is discoverable later.

### 5a) Build a skill map page when the bundle contains many skills

If the archive includes a sizable skill tree (for example multiple ecosystems or 20+ skills), create a dedicated wiki summary page that:
- groups skills by source tree first
- then groups them by capability family
- records the total count per tree and per family
- links into the main skills index/topic map
- adds a small transfer-specific entry in `skill-families.md` or `topic-map.md`

This step is especially useful when the archive contains overlapping ecosystems like Claude, Codex, OpenClaw repo skills, and tool-bundled skills.

### 5b) Copy skills into a namespaced local tree before curation

When importing skills for inspection, prefer copying them into a dedicated namespace such as `~/.hermes/skills/<source-name>/`.

Important details:
- preserve the source tree layout so collisions are easier to inspect
- ignore AppleDouble and macOS metadata files like `._*` and `.DS_Store`
- if the source contains symlink-heavy trees, copy with symlink preservation when appropriate
- do not immediately flatten or merge everything into the active root; curate first, promote later

## 6) Verify the result

Before stopping, confirm:
- the archive path was recorded
- at least the important memory preferences were saved
- copied skill trees are visible under `~/.hermes/skills/`
- the wiki has a transfer page or import note
- any relevant counts or manifests were checked

## Practical heuristics

- Prefer read-only inspection first; do not bulk-import blindly.
- If the archive is large, sample the manifest and the first few memory / skill entries before deciding scope.
- If the bundle includes multiple agents or tool ecosystems, treat their rules as source material, not authoritative Hermes config.
- Use the wiki to preserve structure and evidence, and use memory only for stable conclusions.
- Use skills for reusable operational workflows, not for one-off archive facts.
- When the user wants a skill map, complete it in one pass: build a top-level transfer hub, capability subpages, and leaf skill pages instead of stopping at a single summary page.
- Deduplicate imported skills by source tree and skill name; if the same skill name appears in multiple source trees, disambiguate leaf pages with a category suffix rather than overwriting one with another.
- If a workflow ecosystem is represented only by related subskills and no standalone `SKILL.md`, create a virtual hub page so the wiki graph stays connected.
- After generating the graph, run a wikilink validation pass and fix broken links before stopping.

## Common pitfalls

- Importing temporary task state into permanent memory
- Copying every skill without checking for collisions or duplicates
- Forgetting to strip AppleDouble files (`._*`) from copied archives
- Writing transfer evidence only into chat instead of the wiki
- Treating raw logs or handoffs as canonical facts without validation

## Suggested verification commands

- Inspect archive tree: `tar -tzf <archive> | sed -n '1,200p'`
- Inspect extracted bundle: `find <dir> -maxdepth 2 -type f | sort`
- Count skill trees and memory files
- Validate copied skills exist in `~/.hermes/skills/`
- Check the wiki index and log for a new transfer entry

## When to update this skill

Patch this skill if you discover a better import order, a new archive shape, or a safer deduplication/collision strategy for copied skills.
