---
name: telegram-bot-cutover-and-conflict-check
description: Safely connect a Telegram bot token to a new app or agent. Detect existing webhooks, explain 409 polling conflicts, validate the token, and choose between cutover vs bridge/forwarding.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, bot, webhook, polling, migration, integration, cutover]
---

# Telegram Bot Cutover and Conflict Check

Use this when a user gives you a Telegram bot token and wants to connect the bot to a new system, especially if the bot may already be in use elsewhere.

## When to use
- "接上我的 TG bot"
- "幫我把 Telegram bot 接到新系統"
- Polling returns `409 Conflict`
- The token works, but messages are not arriving in the new app
- You suspect an existing webhook is already attached

## Core lesson
A Telegram bot token may already be bound to an existing webhook. If so:
- `getUpdates` polling will fail with `409 Conflict`
- the right next step is NOT to blindly start polling
- first inspect the live webhook owner and decide cutover strategy

## Procedure

### 1. Validate the token first
Run a simple `getMe` check.

Example:
```bash
node -e 'const t=process.env.TELEGRAM_BOT_TOKEN; fetch(`https://api.telegram.org/bot${t}/getMe`).then(r=>r.json()).then(console.log)'
```

Record:
- bot id
- username
- first_name

### 2. Check whether a webhook already exists
Always inspect webhook state before enabling polling.

Example:
```bash
python3 - <<'PY'
import json, urllib.request, os
T=os.environ['TELEGRAM_BOT_TOKEN']
url=f'https://api.telegram.org/bot{T}/getWebhookInfo'
with urllib.request.urlopen(url, timeout=20) as r:
    print(json.dumps(json.load(r), ensure_ascii=False, indent=2))
PY
```

Look for:
- `url`
- `pending_update_count`
- `last_error_message`
- `allowed_updates`

### 3. Interpret `409 Conflict` correctly
If polling with `getUpdates` returns HTTP 409:
- the bot already has an active webhook
- do NOT keep retrying polling
- do NOT assume the token is broken
- document the current webhook URL and recent webhook errors

### 4. Choose one of two migration paths

#### Path A — Full cutover
Use when the new app should fully own Telegram.
Requirements:
- public HTTPS URL ready
- webhook route implemented and reachable
- secret/allowlist policy ready

Then:
- point Telegram webhook to the new app
- verify a 200 response
- only after success, treat the old owner as retired

#### Path B — Keep current ingress, forward events
Use when the current webhook owner is still the production front door.
Requirements:
- old ingress still working or recoverable
- new app can accept normalized intake/approval events via internal API

Then:
- leave Telegram webhook where it is
- add forwarding from the current ingress into the new system
- cut over later when the new system is stable

This is the safer default during rebuilds.

### 5. Prepare the new app even before public cutover
Even if webhook cutover is not done today, you can still prepare:
- `.env.example` with Telegram settings
- token validation script
- polling script for future/local testing
- internal approval queue route
- intake route
- command parser contract

Recommended env keys:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_MODE`
- `TELEGRAM_ALLOWED_CHAT_IDS`
- `TELEGRAM_ALLOWED_USER_IDS`
- `TELEGRAM_POLLING_TIMEOUT_SECONDS`
- `TELEGRAM_POLLING_LAST_UPDATE_ID_FILE`
- `TELEGRAM_WEBHOOK_URL`
- `TELEGRAM_WEBHOOK_SECRET`
- `APP_BASE_URL`

### 6. Start with a narrow command set
For v1, prefer only:
- `/help`
- `/status`
- `/approvals`
- `/intake <freeform brief>`

If the approval model is already stable enough for operator use, you can extend the v1 command set to:
- `/approve <approvalId>`
- `/changes <approvalId> <note>`
- `/reject <approvalId> <note>`

This works well when:
- approvals already point to exact artifact versions
- every decision appends to an event log
- the bot is acting as a human decision surface rather than an autonomous closer

Delay richer mutation commands until:
- auth/allowlist is clear
- the approval model is stable
- the event log is wired correctly

### 7. Temporary public ingress can unblock first-contact verification
If the user's top priority is simply: "I want to see the bot reply in Telegram right now," a temporary public tunnel can be useful for fast cutover verification.

Practical finding:
- some quick public tunnels may come up but still return unexpected 404s for a Next.js local app
- if one tunnel provider behaves oddly, try a second provider instead of assuming the app route is broken
- in one successful pattern, `localhost.run` worked as a temporary HTTPS public URL after another quick tunnel returned 404 for both `/projects` and the Telegram webhook route

Recommended order for temporary verification:
1. make sure the local app already responds on `http://127.0.0.1:3000`
2. expose it through a temporary HTTPS tunnel
3. verify the public `/projects` page first
4. verify the public Telegram webhook route returns `200` to a test POST with the secret header
5. only then repoint Telegram with `setWebhook`

This is good for rapid first-contact validation, but it is not the final production setup. Replace the temporary URL with a stable domain as soon as possible.

## Safety notes
- Never expose the token in chat output or checked-in files
- Prefer writing the real token only to local `.env.local` or equivalent secret storage
- If a webhook is already in production, treat changing it as a cutover event, not a casual config tweak

## Good user-facing summary
After inspection, report:
1. token validity
2. current webhook owner URL, if any
3. whether polling is blocked by webhook conflict
4. recommended path: cutover now vs keep ingress and forward

## Reusable finding
When a bot is already attached to an existing webhook, the practical order is:
1. validate token
2. inspect webhook
3. confirm whether polling conflicts
4. prepare new app locally
5. cut over only when the new public route is actually ready
