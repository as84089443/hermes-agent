---
name: telegram-local-webhook-cutover
description: Cut a Telegram bot over from an existing webhook to a local development app using a temporary public tunnel, verify delivery, and avoid common tunnel conflicts.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Telegram Local Webhook Cutover

Use when:
- A Telegram bot already exists and is pointed at an old webhook
- You need the bot to start replying from a new local app immediately
- You do not yet have a stable production deployment URL

## Key lesson

In this environment, `cloudflared tunnel --url http://127.0.0.1:3000` produced a public URL but returned `404` for Next.js routes, while `ssh -R 80:localhost:3000 nokey@localhost.run` successfully exposed the local app and allowed Telegram webhook delivery.

Do not assume the first tunnel works just because it prints a URL. Always verify the actual app routes over the public URL before switching Telegram.

## Prerequisites

- Local app is running and responds on localhost (usually port 3000)
- Telegram bot token available
- Webhook handler exists, e.g. `/api/telegram/webhook`
- Optional secret token for `x-telegram-bot-api-secret-token`

## Procedure

### 1. Verify local app first

```bash
curl -I -s http://127.0.0.1:3000/projects | head
curl -i -s http://127.0.0.1:3000/api/telegram/webhook | head
```

Expected:
- `/projects` returns `200`
- webhook route may return `405` on GET if only POST is implemented; that is fine

### 2. Check whether Telegram is already using a webhook

```bash
python3 - <<'PY'
import json, urllib.request
TOKEN='YOUR_BOT_TOKEN'
with urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getWebhookInfo', timeout=30) as r:
    print(r.read().decode())
PY
```

If a webhook already exists, polling will conflict with HTTP 409. Plan a webhook cutover instead of polling.

### 3. Try a temporary public tunnel

Try `cloudflared` only if available, but verify it immediately:

```bash
cloudflared tunnel --logfile /tmp/cloudflared.log --http-host-header localhost:3000 --url http://127.0.0.1:3000
```

Then test:

```bash
curl -I -s 'https://YOUR-TRYCLOUDFLARE-URL/projects' | head
curl -i -s -X POST 'https://YOUR-TRYCLOUDFLARE-URL/api/telegram/webhook' \
  -H 'content-type: application/json' \
  -H 'x-telegram-bot-api-secret-token: YOUR_SECRET' \
  --data '{"update_id":1,"message":{"message_id":1,"chat":{"id":123},"from":{"id":123},"text":""}}' | head
```

If the public route returns `404`, do not use it.

### 4. Preferred fallback: localhost.run reverse SSH tunnel

```bash
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:3000 nokey@localhost.run
```

Look for output like:

```text
https://random-subdomain.lhr.life
```

Verify it really reaches the app:

```bash
curl -I -s 'https://random-subdomain.lhr.life/projects' | head
curl -i -s -X POST 'https://random-subdomain.lhr.life/api/telegram/webhook' \
  -H 'content-type: application/json' \
  -H 'x-telegram-bot-api-secret-token: YOUR_SECRET' \
  --data '{"update_id":1,"message":{"message_id":1,"chat":{"id":123},"from":{"id":123},"text":""}}' | head
```

Expected:
- `/projects` returns `200`
- webhook POST returns `200 {"ok":true}`

### 5. Point Telegram to the new webhook

```bash
python3 - <<'PY'
import json, urllib.request
TOKEN='YOUR_BOT_TOKEN'
url='https://random-subdomain.lhr.life/api/telegram/webhook'
secret='YOUR_SECRET'
req=urllib.request.Request(
    f'https://api.telegram.org/bot{TOKEN}/setWebhook',
    data=json.dumps({'url': url, 'secret_token': secret, 'allowed_updates':['message']}).encode(),
    headers={'Content-Type':'application/json'}
)
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.read().decode())
PY
```

### 6. Verify webhook registration

```bash
python3 - <<'PY'
import urllib.request
TOKEN='YOUR_BOT_TOKEN'
with urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getWebhookInfo', timeout=30) as r:
    print(r.read().decode())
PY
```

Expected:
- `url` matches the new tunnel URL
- `allowed_updates` includes `message`
- `pending_update_count` may be > 0 just after switching; that is normal

### 7. Ask the user to test from Telegram

Best quick tests:
- `/help`
- `/approvals`
- `/intake <freeform brief>`

## Important pitfalls

- A tunnel printing a URL is not proof the app is reachable
- Telegram polling will fail with `409 Conflict` if a webhook is already configured
- `cloudflared` may still return `404` for app routes even when using `--http-host-header localhost:3000`; do not assume that flag fixes Next.js reachability
- localhost.run domains can rotate while the SSH reverse tunnel is still alive; if system output shows a new `*.lhr.life` URL, immediately re-run `setWebhook` to the latest URL
- If the app restarts on a different port, rebuild the tunnel target
- Do not commit `.env.local`; ensure `.env.*` is ignored in `.gitignore`
- When the user sees English pairing copy like "Hi~ I don't recognize you yet", localize it; pairing instructions and approval replies should match the user's language expectations

## Good companion changes

When doing cutover, also:
- add a webhook secret and validate `x-telegram-bot-api-secret-token`
- add a human-readable Telegram response formatter for approvals and decisions
- expose a minimal approval queue endpoint such as `/api/approval-queue`
- localize the unauthorized pairing message if your audience expects Traditional Chinese; the default English pairing copy is easy to misunderstand
- make approval replies use operator language instead of raw IDs/status strings (e.g. explain what decision is needed, what is being reviewed, what the risk is, and exactly which command to send)

A good Telegram approval message should include:
- project name
- what decision is needed in human language
- current status in human language
- what artifact/version is under review
- risk notes
- exact approve / change / reject command examples

## Verification checklist

- Local app responds on localhost
- Public tunnel route returns real app pages, not 404
- Webhook POST returns `200`
- `getWebhookInfo` shows the new URL
- User confirms the bot replies in Telegram
