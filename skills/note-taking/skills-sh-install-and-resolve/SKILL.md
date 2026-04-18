---
name: skills-sh-install-and-resolve
description: Install external skills from skills.sh when the requested skill names are ambiguous, incomplete, or use marketplace names instead of exact package coordinates.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Skills.sh Install and Resolve

Use when:
- The user gives a batch of `npx skills add ...` commands
- Some entries are plain marketplace names like `find-skills`, `frontend-design`, or `technical-writer`
- The first install attempt fails because the string is not a real git repo/package
- You need to install many skills reliably and then summarize what was actually installed

## Core lesson

With `npx skills add`, many human-facing skill names are not valid package coordinates.
Do not trust the raw name. Resolve it first.

Example failure:
- `npx skills add find-skills -y -g`
- Fails with: repository does not exist

Correct pattern:
1. Search with `npx skills find <query>`
2. Extract the best matching `owner/repo@skill`
3. Install that exact package
4. Verify with `npx skills list -g --json`

## Reliable workflow

### 1. Check the CLI first

```bash
command -v npx
npx --version
npx skills --help
```

### 2. Resolve ambiguous names before install

For any plain name, run:

```bash
npx skills find find-skills
npx skills find frontend-design
npx skills find technical-writer
```

Look for output like:

```text
Install with npx skills add <owner/repo@skill>
vercel-labs/skills@find-skills
anthropics/skills@frontend-design
shubhamsaboo/awesome-llm-apps@technical-writer
```

### 3. Prefer explicit coordinates when known

Examples that worked in practice:

- `find-skills` -> `vercel-labs/skills@find-skills`
- `frontend-design` -> `anthropics/skills@frontend-design`
- `web-artifacts-builder` -> `anthropics/skills@web-artifacts-builder`
- `canvas-design` -> `anthropics/skills@canvas-design`
- `theme-factory` -> `anthropics/skills@theme-factory`
- `technical-writer` -> `shubhamsaboo/awesome-llm-apps@technical-writer`
- `memory-intake` -> `nhadaututtheky/neural-memory@memory-intake`
- `memory-audit` -> `nhadaututtheky/neural-memory@memory-audit`
- `memory-evolution` -> `nhadaututtheky/neural-memory@memory-evolution`

For already-explicit entries, install directly, e.g.:

```bash
npx skills add vercel-labs/agent-skills@vercel-react-best-practices -y -g
npx skills add obra/superpowers@writing-plans -y -g
npx skills add wshobson/agents@architecture-patterns -y -g
```

### 4. Batch install carefully

Do not rely on `set -e` with unresolved names in a single giant script unless every item is already normalized.
Safer pattern:
- resolve names first
- then install one-by-one
- record success/failure per item

### 5. Verify final installed set

```bash
npx skills list -g --json
```

Use this as the source of truth, not background process warnings from an earlier failed attempt.

## Important pitfalls

- A background process may report `Installation failed` from the first failed raw-name attempt even though a later resolved pass succeeded.
- Some installed skill names differ from the source folder name, for example:
  - `react-components` may appear as `react:components`
- Global skills may be installed under `~/.agents/skills/` while legacy OpenClaw/Codex skills also exist under `~/.openclaw/skills/` or `~/.codex/skills/`
- Always summarize what actually ended up in `npx skills list -g --json`

## Repo-vs-skill resolution finding
Some user-requested names look like skills but are actually better handled as full repositories or apps.

Observed pattern:
- `Hindsight` resolves cleanly as multiple installable skills from `vectorize-io/hindsight`
- a large repo like `Anthropic-Cybersecurity-Skills` may be installable skill-by-skill, while the full repository is still worth cloning locally for reference
- `Hermes Agent Self-Evolution` and `Hermes Workspace` are not naturally single skills.sh packages; the practical move is to clone the repositories and install/build them directly

Recommended hybrid workflow:
1. Use `npx skills find` for names that sound like marketplace skills
2. Use GitHub repo search when the requested name looks like a full product/repository
3. If it is a full repo, clone it under a neutral location such as `/Users/<user>/dev/external/`
4. Read the repo README/pyproject/package manifest before installing anything
5. Use isolated environments for repo installs:
   - Python repos: create a local `.venv` in that repo
   - Node repos: run `npm install` or the repo's documented package manager in that repo only

Critical environment lesson:
- Do NOT install a repo like `hermes-agent-self-evolution` into the main `hermes-agent` venv unless you explicitly want to mutate Hermes' runtime dependencies.
- In practice this caused dependency drift (`python-dotenv` mismatch) and had to be repaired.
- Safer pattern: create a dedicated repo-local `.venv` first, then install there.

## Good follow-up

After a large batch install:
1. Group the installed skills by capability family
2. Write a summary note in the wiki
3. Highlight the few skills that matter immediately for the current build
4. Call out any risky skills (for example high-risk memory tools) instead of silently treating all installs as equal
5. Explicitly separate:
   - installed marketplace skills
   - cloned reference repos
   - repos successfully built/bootstrapped locally

## Reusable summary structure

When reporting back to the user, include:
- which requested skills were installed
- which source package each ambiguous skill resolved to
- which skills are most relevant right now
- where they fit into the current system or wiki

## Verification checklist

- `npx skills --help` works
- every ambiguous requested name was resolved through `npx skills find`
- installs ran with exact `owner/repo@skill` strings where needed
- `npx skills list -g --json` contains the expected installed skills
- any wiki/catalog integration was updated after install
