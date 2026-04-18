---
name: git-worktree-safe-file-edits
description: Prevent misplaced file-tool writes when working inside a Git worktree by anchoring edits to the actual worktree root and verifying with git status.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, file-editing, verification]
---

# Git worktree-safe file edits

Use this when:
- the repo is using `git worktree`
- the active task must modify files in a specific worktree
- Hermes file tools and terminal may resolve paths differently

## Problem this avoids

A relative `write_file` / `patch` / `read_file` path can land in the parent repo checkout instead of the intended worktree.
This is easy to miss because file-tool reads may still succeed while `git status` inside the worktree shows nothing changed.

## Required workflow

1. Discover the real worktree root
- Run:
  - `pwd`
  - `git rev-parse --show-toplevel`
- Do this in the terminal with the intended `workdir`.

2. Prefer absolute paths for file-tool writes
- For `write_file`, `patch`, and important `read_file` calls, use absolute paths under the intended worktree root.
- Do not rely on relative paths if a worktree is involved.

3. Verify the write landed in the correct checkout
- Immediately run:
  - `git status --short --untracked-files=all`
- Confirm the changed file appears from inside the intended worktree.

4. If the file landed in the wrong checkout
- Search both the main repo root and the worktree for the filename.
- Rewrite the file to the absolute worktree path.
- Remove the misplaced copy from the wrong checkout.
- Re-run `git status --short` in the worktree.

## Minimal command pattern

```bash
pwd
git rev-parse --show-toplevel
git status --short --untracked-files=all
```

## Additional verification learned in practice

When you are editing from a worktree but also running build/typecheck/dev commands:

1. Check whether file-tool writes used the wrong checkout root
- A common signal is:
  - terminal `pwd` is inside `.worktrees/...`
  - but `write_file` with a relative path creates files in the parent repo checkout
- Confirm with absolute-path existence checks if needed.

2. After running `npm run typecheck` or Next.js dev workflows, inspect for incidental generated-file changes
- In this repo shape, `next-env.d.ts` and `tsconfig.tsbuildinfo` may change as side effects.
- If those files are unrelated to the task, restore them before committing:
  - `git restore next-env.d.ts tsconfig.tsbuildinfo`

3. Before commit, re-run `git status --short`
- The worktree should show only the files you intentionally changed.
- This catches both misplaced file-tool writes and unrelated generated-file churn.

## Fast diagnostic signal

If:
- file tools say a file exists
- but `git status` in the target worktree shows no change

then assume the file was probably written to a different checkout until proven otherwise.

## Good practice
- Use file tools for content creation/editing.
- Use terminal for worktree discovery and git-grounded verification.
- Treat `git status` as the source of truth for whether the intended checkout changed.

## Pitfalls
- Mixing relative file-tool paths with worktree-relative terminal commands
- Assuming successful `write_file` means the correct checkout changed
- Forgetting to delete the accidentally written copy in the parent repo

## Done when
- the target file exists under the intended worktree root
- `git status --short` in that worktree shows the expected change
- no duplicate stray copy remains in the parent repo checkout
