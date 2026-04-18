---
name: nextjs-mobile-preview-via-tunnel
description: Expose a local Next.js app to a phone for temporary preview, with validation steps and fallback from cloudflared to localtunnel when external requests return 404.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, preview, mobile, tunnel, cloudflared, localtunnel, qa]
---

# Next.js Mobile Preview via Tunnel

Use when:
- the user is on mobile and cannot see the local desktop browser
- you need a temporary external URL for a local Next.js app
- you must verify the app from a phone before doing real deployment

## Core lesson from this environment

Do NOT assume a public tunnel is working just because it prints a URL.
In this environment:
- `cloudflared tunnel --url http://localhost:3000` successfully created a public URL
- but external requests to the Next.js app returned `404`
- this happened both against the dev server and against `next start`
- local `localhost` still worked fine
- `localtunnel` worked for external preview, but showed a one-time safety interstitial requiring the host IP

Therefore, the reliable workflow here is:
1. verify the local app first
2. prefer a production preview server over `next dev`
3. try tunnel
4. externally validate the tunnel URL
5. if `cloudflared` returns `404`, switch to `localtunnel`

## Recommended workflow

### 1) Verify the local app is actually healthy

Run:

```bash
curl -I http://localhost:3000/projects
```

or if using a production preview port:

```bash
curl -I http://localhost:3002/projects
```

Only proceed if local responses are `200 OK`.

### 2) Prefer production preview over dev server

Build and start a dedicated preview instance:

```bash
npm run build
PORT=3002 npm run start
```

After any UI/content changes that the user needs to check from mobile, rebuild and restart the production preview again before re-sharing the public URL:

```bash
npm run typecheck
npm run build
PORT=3002 npm run start
```

Why:
- separates preview from any existing `next dev`
- avoids dev lock issues
- reduces noise when debugging tunnel problems
- ensures the external mobile preview matches the latest UI text and layout

### 3) Try cloudflared first only if you want the simplest public URL

```bash
cloudflared tunnel --url http://localhost:3002
```

Watch the logs for the generated URL.

Important:
- validate externally with `curl -I https://.../projects`
- if you get `404`, the tunnel exists but is NOT usable for this Next.js preview
- do not tell the user it works until external validation passes
- in this environment, adding `--http-host-header localhost:3000` to `cloudflared` still did NOT fix the external `404`
- once cloudflared fails both plain and host-header attempts, stop burning time and switch to `localtunnel`

### 4) If cloudflared externally returns `404`, switch to localtunnel

Run:

```bash
npx localtunnel --port 3002 --local-host localhost --print-requests
```

Look for output like:

```text
your url is: https://something.loca.lt
```

### 5) Handle the localtunnel safety interstitial

The first browser visit may show a warning page asking for the host IP.
It says:
- “To continue, enter the IP shown above.”

The page also displays the host IP.
The user must enter that IP once per client IP window.

If you need to validate it yourself in the browser tool:
1. open the `loca.lt` URL
2. read the displayed host IP
3. type it into the textbox
4. continue
5. confirm the actual app loads

## Validation checklist

Before giving the user the preview URL, confirm all of these:
- local app returns `200 OK`
- external tunnel URL returns something other than tunnel failure / `404`
- browser can actually load `/projects`
- if using localtunnel, note the IP-gate behavior to the user
- mention that the link is temporary and dies when the local process/tunnel stops

## Known pitfalls

### Pitfall 1: Existing `next dev` lock conflicts
You may see:
- port 3000 already in use
- `.next/dev/lock` cannot be acquired

Do not keep restarting blindly.
Check which instance is already serving and reuse it if healthy.

### Pitfall 2: cloudflared URL exists but app is still unreachable
Symptoms:
- tunnel logs show a valid `trycloudflare.com` URL
- external `curl` returns `404`
- browser shows empty page / no route

Interpretation:
- tunnel transport is up
- Next.js external host handling is not serving the app correctly in this setup
- switch tools instead of debugging forever

### Pitfall 3: localtunnel warning page surprises the user
The `loca.lt` URL may first show a trust/safety warning page.
Do not describe the URL as “directly opens the app” without mentioning this.
Tell the user:
- first open shows a safety page
- enter the displayed host IP once
- then the app opens normally

## Minimal operator message template

Use wording like:

```text
手機可用的臨時預覽網址：
https://something.loca.lt/projects

第一次打開會先看到安全提示頁。
請輸入頁面上要求的 host IP：
X.X.X.X

之後就會進到專案頁。
這是臨時預覽網址；只要本機 preview 或 tunnel 停掉，連結就會失效。
```

## When NOT to use this skill

Do not use this as the final delivery path when:
- the user needs a stable long-lived URL
- the app should be shared broadly with others
- the safety interstitial is unacceptable

In those cases, move to a real preview deployment or a fixed preview domain.
