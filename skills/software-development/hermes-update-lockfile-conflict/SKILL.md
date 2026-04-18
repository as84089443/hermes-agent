---
name: hermes-update-lockfile-conflict
description: Safely run `hermes update` in the hermes-agent repo when the updater auto-stashes local changes and `package-lock.json` conflicts on stash reapply.
---

# Hermes update with package-lock conflict

Use when:
- Running `hermes update` inside the hermes-agent repo
- The updater auto-stashes local changes before pulling/rebasing
- Stash reapply creates a conflict in `package-lock.json`

## Goal
Restore the repo to a clean, usable state without leaving a broken merge conflict in the lockfile.

## Why this happens
`hermes update` may stash local changes automatically. If upstream changed `package-lock.json` and the stashed local lockfile also differs, stash reapply can conflict even when `package.json` itself is fine.

## Workflow
1. Confirm the conflict is limited to the lockfile.
   - Check git status
   - Inspect whether `package.json` is actually conflicted or only `package-lock.json`

2. Reset the conflicted lockfile back to HEAD.
   - `git restore --source=HEAD --staged --worktree package-lock.json`

3. Regenerate the lockfile from the current dependency manifest.
   - `npm install --package-lock-only`

4. Verify the repo is no longer in a conflicted merge/stash state.
   - Check `git status`
   - Confirm no unmerged paths remain

5. If the updater created a temporary stash, compare whether any desired non-lockfile changes still need recovery.
   - Review stash diff carefully
   - If the stash no longer contains anything needed, drop it explicitly

6. Run a lightweight validation if appropriate.
   - Prefer at least `npm install` or project-specific verification if dependency integrity matters

## Commands
```bash
git status
git restore --source=HEAD --staged --worktree package-lock.json
npm install --package-lock-only
git status
git stash list
# if confirmed safe
git stash drop 'stash@{0}'
```

## Verification checklist
- No merge conflict markers remain
- `git status` shows no unmerged files
- `package-lock.json` is regenerated cleanly
- Any temporary stash is either intentionally kept or explicitly dropped

## Pitfalls
- Do not blindly keep the conflicted `package-lock.json`; regenerate it instead.
- Do not drop the stash until you verify whether it contained meaningful non-lockfile work.
- If `package.json` also changed, stop and review dependency intent before regenerating the lockfile.

## Additional findings
- Newer `hermes update` runs may auto-report the exact conflicted files and then reset the working tree back to a clean post-update state while preserving the local work in a named stash plus stash SHA.
- This means conflicts are not always limited to `package-lock.json`; after update, first check whether the updater already recovered to a clean tree and saved the user changes safely in stash before doing any manual conflict surgery.
- If the updater already finished successfully, the safer follow-up is:
  1. `git status` to confirm the repo is clean except for intentional untracked files
  2. `git stash list` / `git stash show --stat stash@{0}` to inspect preserved local work
  3. only then decide whether to `git stash apply` and resolve conflicts manually

## Notes
This is most appropriate when the real conflict is lockfile churn rather than an intentional dependency change, but the first recovery step should now be checking whether `hermes update` already reset the tree and preserved everything in stash.