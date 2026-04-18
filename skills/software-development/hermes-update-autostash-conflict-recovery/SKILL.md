---
name: hermes-update-autostash-conflict-recovery
description: Recover cleanly after `hermes update` succeeds but auto-restoring the updater stash causes multi-file conflicts, especially in web UI pages and config files.
---

# Hermes update autostash conflict recovery

Use when:
- `hermes update` completed the code update, dependency refresh, and restart
- but restoring local changes from the updater-created stash produced conflicts
- especially when conflicts span `web/src/pages/*.tsx`, `hermes_cli/config.py`, or similar app files

## Goal
Restore the user's local work on top of the updated repo without leaving unmerged files or hidden conflict markers.

## Why this is needed
`hermes update` may:
1. auto-stash local changes
2. pull upstream successfully
3. fail when reapplying the stash because upstream changed the same files
4. leave the stash preserved while resetting the worktree clean

In this case, the correct recovery path is to manually apply the preserved stash, resolve conflicts intentionally, stage the resolutions, and verify with a targeted build.

## Required workflow

1. Confirm repo root and stash state
```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git stash list | head -n 5
git stash show --name-only stash@{0}
```

2. Apply the preserved updater stash
```bash
git stash apply stash@{0}
```
Expect non-zero exit if conflicts occur.

3. Inspect conflicted files
```bash
git diff --name-only --diff-filter=U
```
For each conflicted file, inspect the diff:
```bash
git diff -- path/to/file
```

4. Merge with intent, not mechanically
Typical merge rules learned from practice:
- Keep user-facing Traditional Chinese copy if that was the local customization intent.
- Keep new upstream data shapes and API fields if upstream introduced them.
- Prefer merged results that preserve both:
  - upstream structural changes
  - local UX/content improvements
- If a file was accidentally rewritten while resolving, compare to `HEAD` and rebuild the desired merged version rather than keeping a giant accidental diff.

Useful comparison commands:
```bash
git show HEAD:path/to/file

git show stash@{0}:path/to/file
```

5. Stage resolved files explicitly
Important: even after conflict markers are removed from file contents, Git still reports `UU` until the resolutions are staged.
```bash
git add path/to/resolved-file ...
```

6. Verify there are no remaining conflict markers
```bash
rg -n '^(<<<<<<<|=======|>>>>>>> )' path1 path2 ... || true
```

7. Run syntax/build validation in the correct subproject
Important finding: the web build lives under `web/`, not the repo root.
```bash
cd web && npm run build
```
Do not use `npm run build` at the repo root unless package.json there actually defines it.

8. Run whitespace/conflict hygiene checks
```bash
git diff --check
git diff --cached --check
```
If these report blank-line-at-EOF or similar formatting issues, fix them and re-stage.

9. Confirm final state
```bash
git status --short --branch
git stash list | head -n 5
```
At this point:
- no `UU` entries should remain
- restored local modifications should appear as normal `M` entries
- stash can be kept temporarily as a safety backup until the user confirms

10. If you need to summarize or commit the recovered work, check the right diff view
Important finding: after conflict resolution, changes may already be staged. In that case `git diff` can look empty even though there is recovered work ready to commit.
```bash
git status --short --branch
git diff --cached --stat
git diff --cached --name-only
```
Use `git diff --cached` for review/commit summaries when the recovered files have been staged.

11. Optional closeout after verification
If the user wants the recovery fully closed out:
```bash
# targeted tests/build as appropriate
cd web && npm run build

# if desired, commit only the recovered tracked changes
git commit -m "[verified] <recovered-change-summary>"

# only after the user confirms the recovery is good
git stash drop stash@{0}
```
Be careful not to accidentally include unrelated untracked docs/specs/scripts that were not part of the recovered tracked changes.

## Heuristics for common Hermes web conflicts

### `hermes_cli/config.py`
- If conflict is only copy/description text, reconstruct from `HEAD` and re-apply the desired wording surgically.
- This avoids accidentally replacing large sections of the config file and creating a huge diff.

### `web/src/pages/AnalyticsPage.tsx`
- Preserve upstream API compatibility and any newly added metrics fields.
- Preserve local Traditional Chinese labels and any useful analytics cards/tooltips.
- Verify by running the web build.

### `web/src/pages/CronPage.tsx`
- Prefer upstream field names/types (`job.state`, structured schedule data) if API changed.
- Reapply local Traditional Chinese labels on top.

### `web/src/pages/EnvPage.tsx`
- Keep upstream-added components like OAuth provider sections if they are new functionality.
- Reapply localized section comments/labels as needed.

### `web/src/pages/SessionsPage.tsx`
- Watch for corrupted identifiers from partial manual merges.
- Preserve upstream pagination/API changes if `getSessions()` now returns paginated data.
- Reapply localized labels after structural correctness is restored.

### `web/src/pages/StatusPage.tsx`
- Prefer upstream responsive layout improvements.
- Reapply local localized labels and fallback text.

## Verification checklist
- `git status` shows no unmerged paths
- no conflict markers remain in resolved files
- `cd web && npm run build` succeeds
- `git diff --check` and `git diff --cached --check` both pass
- stash is intentionally kept or intentionally dropped

## Pitfalls
- Removing conflict markers but forgetting `git add`, leaving files in `UU`
- Running `npm run build` from repo root instead of `web/`
- Blindly taking either upstream or stash version when both contain useful changes
- Accidentally rewriting a large file during resolution; recover from `git show HEAD:file` and reconstruct the intended merged result
- Dropping the updater stash too early before confirming the recovered work is correct
