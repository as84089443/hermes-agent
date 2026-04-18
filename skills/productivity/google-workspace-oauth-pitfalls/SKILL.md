---
name: google-workspace-oauth-pitfalls
description: Fix common Google Workspace OAuth setup failures in Hermes, especially localhost callback errors and local skill script import issues.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [google, oauth, workspace, setup, troubleshooting]
    related_skills: [google-workspace]
---

# Google Workspace OAuth pitfalls for Hermes

Use this when:
- `google-workspace` skill setup is failing in a real Hermes profile
- The user completed Google consent but the browser shows an error page
- `setup.py` cannot import `hermes_constants`
- The user expects browser automation to finish Google login but the available browser is isolated from their local logged-in browser

## Key findings

1. The Hermes/browser tool may be controlling an isolated remote browser session, not the user's local browser.
- Do not assume a Google login completed in the user's own browser is visible to the browser tool.
- If local login is already available, the fastest path is often:
  - generate the OAuth URL in terminal
  - have the user open it in their own browser
  - have them paste back the final redirect URL

2. `setup.py` may fail with `ModuleNotFoundError: hermes_constants` when run from the skill directory.
- Run it with `PYTHONPATH` pointed at the hermes-agent repo root.

Canonical pattern:
```bash
source venv/bin/activate
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="$(pwd)/venv/bin/python"
PYTHONPATH="$(pwd)" "$PYTHON_BIN" "$GWORKSPACE_SKILL_DIR/scripts/setup.py" --check
```

3. The OAuth redirect uses `http://localhost:1` and some browsers show `ERR_UNSAFE_PORT`.
- This is not fatal.
- Tell the user to copy the full redirect URL from the browser address bar.
- Pass that full URL directly to `--auth-code`; the script can parse out `code` and `state`.

Example:
```bash
PYTHONPATH="$(pwd)" "$PYTHON_BIN" "$GWORKSPACE_SKILL_DIR/scripts/setup.py" --auth-code "http://localhost:1/?state=...&code=..."
```

4. After OAuth succeeds, API access may still fail because the Google Cloud project has not enabled the API yet.
- Typical error: `SERVICE_DISABLED` / `accessNotConfigured`
- Have the user enable the needed APIs in Google Cloud Console, then retry.
- For calendar analysis, at minimum enable Google Calendar API.

## Recommended real-world flow

1. Install `gws`
2. Save `client_secret.json`
3. Generate auth URL in terminal
4. User opens URL in their own browser
5. User completes consent and pastes back the final localhost redirect URL even if the page errors
6. Exchange with `--auth-code`
7. Verify with `--check`
8. If API calls fail, enable the missing Google API in Cloud Console and retry

## Why save this

These failures are easy to misdiagnose as bad OAuth or bad credentials, but in practice they often come from:
- isolated browser sessions
- localhost unsafe-port behavior
- missing `PYTHONPATH`
- disabled Google APIs after successful auth
