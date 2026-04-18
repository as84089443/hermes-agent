---
name: thinking-hound-mode
description: |
  Opt-in execution discipline adapted from asterwei416/thinking-hound-mode. Trigger when the user explicitly asks for "thinking-hound mode", "思維獵犬模式", "獵犬模式", or wants planner-vs-execution routing, aggressive latest-doc research, a braking checkpoint before large feature work, or red/blue-team hardening. This skill is additive only: it must not override higher-priority OpenClaw system, repo, safety, or canonical-path rules.
---

# thinking-hound-mode

This skill adapts the upstream "Thinking Hound Mode" into an OpenClaw-compatible local skill.

It is intentionally packaged as an **opt-in mode**, not a global persona override.

## Core Contract

1. Higher-priority instructions always win.
   Follow OpenClaw `SYSTEM.md`, repo `AGENTS.md`, canonical-path rules, and any active system/developer instructions before applying upstream behavior.
2. Use this skill only when it clearly matches the request.
   Do not silently force every task into hound mode.
3. Keep the behavior proportional.
   Use Planner Mode for large or high-risk work, and Execution Mode for narrow, well-bounded tasks.

## Mode Routing

### Planner Mode

Use Planner Mode when the task involves any of the following:

- new features with multiple moving parts
- architecture changes across modules
- schema / contract / migration work
- broad refactors with unclear blast radius
- tasks where the user explicitly wants a spec, plan, or approval gate first

Planner Mode workflow:

1. Inspect the codebase and current constraints first.
2. Research latest official docs for third-party tools or libraries when the answer could be time-sensitive.
3. Produce a compact spec, assumptions, risks, and a Markdown task list.
4. End with an explicit approval gate such as:
   `[等待授權] 以上規格與計畫是否符合預期？可以開始實作了嗎？`
5. Stop before editing implementation files.

### Execution Mode

Use Execution Mode when the task is narrow and bounded, for example:

- a targeted bug fix
- a localized UI tweak
- a small automation or script adjustment
- a direct "幫我直接做" request where the blast radius is limited

Execution Mode workflow:

1. Briefly tell the user what you are about to change.
2. Inspect the relevant files before editing.
3. Implement in small increments.
4. Verify with real commands, tests, or runtime checks.
5. Before finalizing, run a short red/blue review against nulls, invalid input, dependency failure, and regression risk.

## Research Standard

When the task depends on third-party packages, frameworks, UI kits, APIs, or other fast-moving technology:

- fetch the latest official docs before implementation
- prefer primary sources over summaries
- verify version-sensitive behavior instead of relying on stale memory

Do not browse just to restate stable local facts that are already in the repo.

## UI / UX Rule

For frontend, component, or interaction work:

1. Read [references/ui.instructions.md](./references/ui.instructions.md).
2. Also fetch current official UI library docs when the component API or accessibility guidance may have changed.
3. Check for accessibility basics, interactive states, and performance impact.

## Upstream Reference

Read these only when needed:

- [references/upstream-summary.md](./references/upstream-summary.md) for the upstream philosophy and OpenClaw adaptation notes
- [references/ui.instructions.md](./references/ui.instructions.md) for UI constitution details
- [references/evolution-protocol.md](./references/evolution-protocol.md) when updating documentation for this mode itself

## Boundaries

- This skill does not grant permission to ignore approval requirements already present in the current environment.
- This skill does not replace repository logging, verification, or bridge-write obligations.
- This skill should strengthen judgment and research discipline, not create unnecessary ceremony.
