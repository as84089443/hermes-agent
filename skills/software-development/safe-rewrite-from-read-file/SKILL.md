---
name: safe-rewrite-from-read-file
description: Prevent corrupting source files when rewriting content copied from Hermes read_file output, which prefixes every line with line numbers like `12|content`.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [file-editing, debugging, safety, read-file, write-file]
---

# Safe Rewrite from read_file Output

## When to use

Use this when:
- you plan to rewrite a file using content previously obtained from `read_file`
- you are composing a new whole-file `write_file` payload from file-tool output
- you are copying blocks from `read_file` into `execute_code` or string templates
- a file suddenly shows syntax errors after a rewrite and the top of the file looks like `1|import ...`

## Core risk

`read_file` is a viewing format, not a byte-for-byte source dump.
It can transform source in at least two ways:
- line prefixes like `1|import ...`
- redacted secret-like values such as `***` or `secret...(32)`

Those transformations are for safe display. They are NOT valid source content.

If you pass `read_file` output back into `write_file`, `execute_code`, or whole-file reconstruction logic, you can corrupt the file even after stripping line numbers.

Typical failure modes:
- parser errors because `1|...` got written into the file
- syntax/runtime errors because a real expression was replaced by a redacted placeholder like `***`
- partially truncated tokens or URLs turning valid code into invalid code

## Safe rules

1. Never treat `read_file.content` as raw source without stripping `^\s*\d+\|` prefixes.
2. Never use `read_file` as the source for whole-file rewrites on files that may contain secrets, tokens, OAuth constants, URLs, or other redaction-sensitive literals.
3. For sensitive or runtime-critical files, prefer:
- `patch` for targeted edits
- `terminal`/git restore when recovery is needed
- re-reading from the actual file inside Python only when you are certain you are not consuming display-redacted tool output
4. For large rewrites, prefer:
- `patch` for targeted edits
- `read_file` only for inspection
- `write_file` only when you have clean, reconstructed source text from a trusted raw source
5. After any whole-file rewrite sourced from tool output:
- immediately run typecheck/build/syntax validation
6. If a file suddenly shows syntax errors around placeholders like `***` or `secret...(32)`, inspect whether tool-output redaction was written back into the source.

## Safe patterns

### Pattern A — targeted change
Use `patch` instead of rebuilding the whole file.

### Pattern B — whole-file rewrite
If you must rewrite:
- reconstruct the file manually from clean strings
- or strip line prefixes programmatically before writing

Example strip logic:

```python
clean = "\n".join(
    line.split("|", 1)[1] if "|" in line and line.split("|", 1)[0].strip().isdigit() else line
    for line in text.splitlines()
)
```

## Recovery pattern

If corruption already happened:
1. inspect the file start with `read_file`
2. confirm whether either happened:
   - numbered prefixes were written into the file
   - redacted placeholders like `***` / `secret...(32)` were written into the file
3. restore from git or another trusted raw source when possible
4. avoid "patching the patch" repeatedly if many placeholders leaked in — full restore is often safer
5. reconstruct only the intended change on top of the clean file
6. rerun typecheck/build
7. only then continue feature work

## Verification

After repair or rewrite, run the project's real checks, for example:
- `npm run typecheck`
- `npm run build`
- `python -m py_compile ...`

## Remember

`read_file` is a viewing format, not a raw file dump.
If you rewrite from it blindly, you will write the line numbers into the source.
