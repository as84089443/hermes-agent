---
name: telegram-webhook-cutover-via-localhostrun
description: Cut a Telegram bot over to a local app using localhost.run when no stable public HTTPS URL exists yet. Includes conflict checks, webhook reset, localhost.run tunnel extraction, secret-token setup, and verification.
---

# Telegram Webhook Cutover via localhost.run

Use when:
- A Telegram bot already exists and has a token
- The local app is running on localhost
- There is no stable public HTTPS deployment yet
- Polling is blocked because an existing webhook is active
- You need the user to test the bot immediately in Telegram

Do NOT use when:
- A stable production URL already exists (use that directly)
- The app is not responding locally yet

## Why this skill exists

In practice:
- Telegram `getUpdates` returns `409 Conflict` if a webhook is already configured
- Quick Cloudflare tunnels may come up but still return 404 for the forwarded app path in some environments
- `localhost.run` SSH reverse tunnels worked reliably for exposing the local Next.js app
- The localhost.run hostname can change mid-session, so you must re-run `setWebhook` whenever the tunnel URL changes

## Inputs needed

- `TELEGRAM_BOT_TOKEN`
- Local app port (default usually `3000`)
- A webhook route in the app, e.g. `/api/telegram/webhook`
- A webhook secret token value

## Workflow

### 1. Verify the local app is alive

Check the app first:

```bash
curl -I -s http://127.0.0.1:3000/
curl -I -s http://127.0.0.1:3000/api/telegram/webhook
```

Expected:
- App route returns `200` or equivalent success
- Webhook route may return `405 Method Not Allowed` on GET, which is acceptable if it only supports POST

### 2. Inspect current Telegram webhook state

```bash
python3 - <<'PY'
import json, urllib.request
TOKEN='YOUR_BOT_TOKEN'
with urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getWebhookInfo', timeout=30) as r:
    print(r.read().decode())
PY
```

Look for:
- current `url`
- `pending_update_count`
- recent `last_error_message`

Important:
- If a webhook already exists, polling will conflict until the webhook is removed or replaced

### 3. Generate a webhook secret

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(24))
PY
```

Store this in the app env, e.g. `TELEGRAM_WEBHOOK_SECRET`.

### 4. Start a localhost.run tunnel

Use localhost.run instead of Cloudflare quick tunnel if Cloudflare path forwarding is unreliable.

```bash
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:3000 nokey@localhost.run
```

Watch stdout for a line like:

```text
abcd1234.lhr.life tunneled with tls termination, https://abcd1234.lhr.life
```

That HTTPS domain is the public base URL.

Notes:
- Keep this SSH process running
- localhost.run may emit a fresh HTTPS hostname later even from the same long-lived SSH session/process
- treat every newly printed `https://...lhr.life` line as a possible cutover event
- when that happens, immediately re-verify `/projects` and the webhook POST on the new hostname, then re-run Telegram `setWebhook`
- if you do not update the webhook, Telegram will keep calling the old hostname and the bot will appear flaky even though localhost is healthy

### 5. Verify the tunnel really reaches the app

Before switching Telegram, test both the app and webhook path through the public URL:

```bash
curl -I -s 'https://abcd1234.lhr.life/projects'
curl -i -s -X POST 'https://abcd1234.lhr.life/api/telegram/webhook' \
  -H 'content-type: application/json' \
  -H 'x-telegram-bot-api-secret-token: YOUR_SECRET' \
  --data '{"update_id":1,"message":{"message_id":1,"chat":{"id":123456},"from":{"id":123456},"text":""}}'
```

Expected:
- App route returns `200`
- Webhook route returns `200` with JSON like `{"ok":true}`

If the public path returns `404`, do NOT cut over yet.

### 6. Point Telegram to the new webhook

```bash
python3 - <<'PY'
import json, urllib.request
TOKEN='YOUR_BOT_TOKEN'
url='https://abcd1234.lhr.life/api/telegram/webhook'
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

Then verify:

```bash
python3 - <<'PY'
import urllib.request
TOKEN='YOUR_BOT_TOKEN'
with urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getWebhookInfo', timeout=30) as r:
    print(r.read().decode())
PY
```

Expected:
- `url` matches the localhost.run URL
- `pending_update_count` is small or zero

### 7. Ask the user to test in Telegram

Best first commands:
- `/help`
- `/status`
- `/approvals`
- `/intake ...`

If pairing is enabled, the user may first receive a pairing code. Approve it via:

```bash
hermes pairing approve telegram CODE
```

### 8. If localhost.run rotates to a new hostname

Repeat only these steps:
1. capture the new HTTPS hostname from SSH output
2. verify the new URL reaches the app
3. run `setWebhook` again with the new URL
4. verify with `getWebhookInfo`

## App-side requirements

The webhook handler should:
- accept POST only
- validate `x-telegram-bot-api-secret-token` if configured
- parse message updates
- return JSON success quickly

Recommended env variables:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `TELEGRAM_WEBHOOK_URL`
- `APP_BASE_URL`

## Troubleshooting

### `409 Conflict` from getUpdates
Cause:
- A webhook is active

Fix:
- Replace or remove the webhook before using polling

### Telegram webhook shows `502 Bad Gateway`
Cause:
- Existing upstream is broken

Fix:
- Cut over to the new working localhost.run URL after verifying public reachability

### Cloudflare quick tunnel gives public 404s
Observed fix:
- Switch to localhost.run reverse tunnel instead

### Tunnel URL changed unexpectedly
Fix:
- Re-run `setWebhook` with the new hostname

## Verification checklist

- [ ] local app responds on localhost
- [ ] public localhost.run URL responds on a real app route
- [ ] public webhook path responds to POST
- [ ] Telegram `setWebhook` succeeded
- [ ] Telegram `getWebhookInfo` matches the current tunnel URL
- [ ] user received a real bot reply in Telegram

## Output format to user

Keep the user-facing summary concise:
- webhook switched
- current public URL
- what to type in Telegram now
- whether pairing is still required
