---
name: hermes-skills-zh-localization-and-wiki-distillation
description: Localize Hermes CLI slash/skill autocomplete annotations into Traditional Chinese, then rebuild the live skills inventory into Brian's wiki with operator guide, catalog, family summary, and visual map.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, cli, autocomplete, localization, wiki, obsidian, mermaid]
---

# Hermes skills zh localization and wiki distillation

Use when:
- the user wants `/` autocomplete comments in Hermes CLI shown in Chinese
- the installed skills feel too numerous / unstructured
- the user wants the live skill inventory distilled into the wiki
- the user wants a visual skill map in Obsidian

## Outcome

1. Built-in slash command descriptions show Traditional Chinese in autocomplete/help metadata.
2. Skill slash commands show Chinese metadata too.
3. If a skill has no explicit Chinese description, do not stop at `技能：<name>（<category zh>）`.
   Generate a short Traditional Chinese fallback in this shape:
   `做什麼：...；適合：...`
   Prefer keyword-based hints from the English description first, then fall back to category-level defaults.
4. For the highest-leverage imported skills, do one more layer beyond fallback generation:
   verify the upstream GitHub repo / README and write curated repo-grounded zh hints so important skills are not misclassified by a shallow local description.
   This is especially important for donor/framework-style skills like `gstack`, `web-access`, and `thinking-hound-mode`.
5. The wiki gets refreshed from the real `~/.hermes/skills/` inventory, not stale counts.
6. Obsidian gets a readable visual map via Mermaid.

## Files to modify

### CLI localization
- `hermes_cli/commands.py`
- `agent/skill_commands.py`
- `tests/hermes_cli/test_commands.py`
- `tests/agent/test_skill_commands.py`

### Wiki outputs
- `~/wiki/concepts/skills-operator-guide.md`
- `~/wiki/concepts/skills-catalog.md`
- `~/wiki/concepts/skill-families.md`
- `~/wiki/operations/skills-visual-map.md`
- `~/wiki/index.md`
- `~/wiki/log.md`

## Recommended execution pattern

### 1. Work in an isolated git worktree
Do not edit the user's dirty main checkout directly.

```bash
git fetch origin main
git worktree add -b skill-zh-distill /tmp/hermes-skill-zh origin/main
cd /tmp/hermes-skill-zh
pwd
git rev-parse --show-toplevel
git status --short --untracked-files=all
```

### 2. Localize built-in slash command metadata
In `hermes_cli/commands.py`:

- add a `COMMAND_DESCRIPTIONS_ZH` mapping keyed by canonical command name
- add `_localized_command_description(cmd)`
- make `_build_description()` use the zh text for CLI-facing descriptions
- make alias text render in zh too

Important: keep the command names themselves unchanged. Only localize the annotation/description layer.

### 3. Localize skill autocomplete metadata
In `agent/skill_commands.py`:

- add category slug -> zh label mapping
- detect skill category from the relative skill path
- allow explicit `zh_description` in frontmatter to override fallback
- store `zh_description` and `category` in `_skill_commands`
- build generated zh fallback descriptions from two layers:
  - keyword hints inferred from the English description, e.g. Slack / GitHub / browser / QA / design / plan / wiki / PDF / deploy
  - category defaults when no useful keyword is found

Recommended fallback output shape:
- `做什麼：<一句中文用途>；適合：<一句中文使用時機>`

If the source description already contains CJK text, keep it compact and wrap it as:
- `做什麼：<截短後原描述>；適合：任務明確對到這個技能名稱或描述時`

In `hermes_cli/commands.py` skill completion rendering:

- prefer `info['zh_description']`
- fallback to `info['description']`
- final fallback to `技能指令`

This keeps old skills working without mass-editing 200+ skill files.

## Skill frontmatter convention learned
If you want a hand-authored Chinese tooltip for a specific skill, support either:

```yaml
zh_description: 思維獵犬模式（規劃／執行節奏控制）
```

or later, if needed, a nested metadata variant.

But do not require this for all skills. Auto-fallback is the scalable default.

## 4. Rebuild the wiki from the live skills inventory
Do not hand-maintain counts when the skill tree is large.

Use code to scan `~/.hermes/skills/**/SKILL.md`, parse minimal frontmatter, and rebuild:

- `skills-catalog.md` — full inventory with path
- `skill-families.md` — grouped family summary with counts and representative skills
- `skills-operator-guide.md` — Brian-facing shortlist / routing guide
- `skills-visual-map.md` — Mermaid visual map for Obsidian

Important: write catalog/family pages from the real inventory so counts stay correct.

## 5. Visual map strategy
For a quick useful visual map, Mermaid in markdown is enough.

Put it at:
- `~/wiki/operations/skills-visual-map.md`

Include:
- core delivery skills
- GitHub / ship cluster
- boss-mode / control-plane cluster
- web / QA cluster
- knowledge / workspace cluster
- OpenClaw transfer donor cluster

Also explain where to view it:
- open the page directly in Obsidian reading mode
- or use Obsidian Graph View for overall note relationships

## 6. Tests to run
From the repo root:

```bash
source /Users/brian/dev/hermes-agent/venv/bin/activate
python -m pytest tests/hermes_cli/test_commands.py tests/agent/test_skill_commands.py -q
```

Expected pattern:
- all tests pass
- update assertions for zh metadata text where needed

## 7. Landing pattern
If you worked in a temporary worktree:

```bash
git add agent/skill_commands.py hermes_cli/commands.py tests/agent/test_skill_commands.py tests/hermes_cli/test_commands.py
git commit -m "feat: localize slash skill hints and distill skill inventory"
```

Then cherry-pick or otherwise port the commit into the active main repo if that is the desired landing place.

Re-run the same focused pytest suite in the target repo after cherry-picking.

## Pitfalls

### 1. Verify high-leverage donor skills against their upstream GitHub before classifying them
Do not classify a well-known imported skill only from the local short description if that skill is actually a larger framework.

Concrete lesson learned:
- `gstack` looked like a browser/QA helper if you only read the short skill description.
- But after checking `https://github.com/garrytan/gstack`, it is really a higher-level software-factory / sprint-method package that contains many roles (`office-hours`, `plan-*`, `review`, `qa`, `ship`, `browse`, etc.).
- So in the wiki and operator guide, classify `gstack` as an upper-layer framework for large workstreams, not merely a browser utility.

Rule:
- for any "important" or potentially high-leverage imported skill, fetch the upstream README / repo description before writing the operator guide or family summary
- especially do this for donor skills from `openclaw-transfer`

### 2. Don’t localize command slugs
Only localize descriptions. `/help` should stay `/help`, not become `/幫助`.

### 2. Don’t require per-skill manual zh text
There may be 200+ skills. Use fallback generation so the system scales.

### 3. Don’t trust stale wiki counts
Always rescan `~/.hermes/skills/` and regenerate catalog/family pages when doing a cleanup pass.

### 4. Prefer worktrees when the main repo is dirty
This task often happens while the main checkout already contains unrelated work.

### 5. Remember process restart reality
CLI autocomplete changes usually require starting a fresh Hermes process to observe them reliably.

## Verification checklist
- [ ] `/help` style built-ins show Chinese description metadata in autocomplete tests
- [ ] skill slash completions prefer `zh_description` when available
- [ ] skill slash completions fall back to `做什麼：...；適合：...`
- [ ] generated fallback prefers keyword hints before category-only defaults
- [ ] `skills-catalog.md` reflects current live skill count
- [ ] `skill-families.md` is rebuilt from the same scan
- [ ] `skills-visual-map.md` exists and renders as Mermaid in Obsidian
- [ ] `index.md` links the new skills pages
- [ ] `log.md` records the rebuild

## Good default operator shortlist for Brian
When rebuilding `skills-operator-guide.md`, emphasize these as the default high-leverage set:

- `thinking-hound-mode`
- `writing-plans`
- `subagent-driven-development`
- `systematic-debugging`
- `requesting-code-review`
- `test-driven-development`
- `phase-based-autonomous-delivery`
- `github-pr-workflow`
- `github-code-review`
- `web-access`
- `gstack`
- `playwright`
- `dogfood`
- `boss-mode-mobile-decision-ui`
- `hermes-dashboard-project-control-plane`
- `slack-mcp-boss-mode-control-layer`

These cover most daily work without treating the whole skill inventory as a flat choice set.
