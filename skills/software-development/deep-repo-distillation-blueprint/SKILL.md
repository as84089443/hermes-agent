---
name: deep-repo-distillation-blueprint
description: Deep-study one or more repos over multiple rounds, separate real substance from README mythology, and turn the findings into a concrete upgrade or rebuild blueprint.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, architecture, distillation, blueprint, repos]
---

# Deep Repo Distillation Blueprint

Use when:
- the user wants serious repeated study of a repo, not a quick summary
- multiple repos should be cross-synthesized into an upgrade path
- README-level impressions are likely to be misleading
- the output should become an actionable architecture or implementation blueprint

## Core rule
Do not stop at README or top-level docs.
Research in rounds and only promote conclusions that survive source-level checks.

## Recommended round structure

### Round 1 — Surface map
- Read README, top-level docs, architecture pages, usage docs
- Identify the repo's claimed core ideas
- Write down hypotheses, not conclusions

### Round 2 — Core source verification
- Inspect the implementation files that should carry the claimed ideas
- Check write path, query path, state path, recovery path, or closeout path depending on repo type
- Confirm which claims are materially real vs merely described

### Round 3 — Maturity gap analysis
- Find where docs overstate maturity
- Look for stubs, shallow integrations, test-only paths, or policy skeletons not fully wired into runtime
- Distinguish "visible but not integrated" from "truly production-central"

### Round 4+ — Cross-synthesis
For multiple repos:
- identify what each repo actually solves
- identify what they do not solve
- identify what to copy directly, adapt carefully, and reject

## Hard questions to ask during source-level study
- Is this capability real in code, or only asserted in docs?
- Is it central to runtime, or only present in tests/policy files?
- Does the system resolve conflicts, or only surface them?
- Is explainability a trust layer, or just debug output?
- Is recovery actually connected to the main loop, or only available as a recipe?
- Is parity backed by deterministic scenarios, or mostly narrative documentation?

## Output pattern
Always produce these layers:

1. Raw source notes
- capture repo-specific evidence pages or file paths
- keep them as research artifacts

2. Distillation page
- what is genuinely valuable
- what is hype or overstatement
- what is reusable

3. Upgrade blueprint
- current-state diagnosis of the target system
- top upgrade cuts
- target architecture
- workstreams
- sequencing
- risk register
- verification matrix
- anti-hype challenge pass

4. Phase-1 lock package (required when the target design introduces layered state, layered memory, or multiple sources of truth)
- define layer boundaries before implementation
- define source-of-truth ownership per layer
- define category taxonomy / routing rules
- define promotion / demotion rules
- define retrieval trigger matrix
- define red-team guardrails against split-brain, scope leakage, and prompt bloat

Do not jump from blueprint straight to code when ownership and promotion rules are still ambiguous.

## Anti-hype challenge pass
Before finalizing, explicitly write:
- where repo A overstates maturity
- where repo B overstates maturity
- what this means for the target system

This step is mandatory. It prevents cargo-cult adoption.

## Progress visibility rule
If the user asked to see ongoing research progress, send heartbeat updates with:
- 目前主 phase
- 剛完成什麼
- 現在阻塞
- 下一個 join point

## Reusable heuristics
- Prefer source-level truth over branding
- Prefer narrow, proven slices over giant abstract frameworks
- Copy discipline, not mythology
- Treat tested policy skeletons and integrated runtime systems as different maturity levels
- Turn research into a canonical blueprint before implementation starts

## Good final deliverable standard
The blueprint is complete when it includes:
- diagnosis
- top upgrade sequence
- detailed workstreams
- copy/adapt/reject judgments
- risk notes
- verification matrix
- target architecture
- milestone sequencing
- anti-hype correction layer
