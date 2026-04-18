# Upstream Summary

Source repository:

- <https://github.com/asterwei416/thinking-hound-mode>

Primary upstream files:

- `thinking-hound-mode.agent.md`
- `ui.instructions.md`
- `evolution-protocol.md`

## What the upstream mode emphasizes

1. Adaptive routing between planning and execution.
   Large feature work should stop at a formal planning checkpoint and wait for approval.
2. Recursive web research.
   Fast-moving dependencies should be verified against current docs instead of relying on older model knowledge.
3. UI constitution.
   Frontend work should consult design and accessibility guidance rather than emitting default framework output.
4. Red/blue-team hardening.
   Proposed solutions should be attacked from failure-case and adversarial angles before being considered complete.
5. Continuous evolution.
   Important patterns and improvements should be documented instead of being lost between sessions.

## OpenClaw adaptation notes

This local skill intentionally does **not** copy the upstream persona wholesale.

Instead, it converts the useful parts into an OpenClaw-safe workflow:

- opt-in skill instead of global replacement
- OpenClaw `SYSTEM.md` and repo instructions remain higher priority
- planner gate is used for large or high-risk work, not every task
- execution remains fast for narrow bug fixes and direct edits
- latest-doc research is used when the topic is time-sensitive

If you want to refresh this skill from upstream later, compare the latest upstream Markdown files against this wrapper and update the local references accordingly.
