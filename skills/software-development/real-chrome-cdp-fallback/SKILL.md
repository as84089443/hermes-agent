---
name: real-chrome-cdp-fallback
description: Attach to the user's real Google Chrome on macOS via Chrome DevTools Protocol when Hermes/browser skills are stuck in an isolated session or gstack browse is blocked.
---

# Real Chrome CDP Fallback

Use when:
- Hermes `browser_navigate` opens pages, but they do not appear in the user's visible Chrome
- The user says they already logged in in Chrome and wants the agent to use that session
- gstack/OpenClaw browse binaries fail or get killed on macOS
- Cookie import is flaky and you need the real logged-in browser now

## What this solves

Some browser tools silently run in their own local/headless session. That means:
- your navigation works
- but it does **not** touch the user's visible Chrome
- and it does **not** inherit the user's real login state

This skill verifies that failure mode, then switches to a direct CDP attach flow that controls the real Chrome.

## Fast diagnosis

First, check whether Chrome remote debugging is already up:

```bash
python - <<'PY'
import socket
for port in [9222, 9229]:
    s=socket.socket(); s.settimeout(2)
    try:
        s.connect(('127.0.0.1', port)); print(port, 'open')
    except Exception as e:
        print(port, 'closed', e)
    finally:
        s.close()
PY
```

If 9222 is open, inspect CDP:

```bash
curl -s http://127.0.0.1:9222/json/version
curl -s http://127.0.0.1:9222/json/list | head -40
```

## Launch a real Chrome debug instance on macOS

If 9222 is not open, launch Chrome directly. Prefer the actual binary path, not `open -a`, because `open -a "Google Chrome" --args ...` can report success while the debug port never comes up. Direct binary launch is more reliable for remote debugging.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check \
  >/tmp/hermes-chrome-debug.log 2>&1 &
```

Then verify:

```bash
curl -s http://127.0.0.1:9222/json/version
cat /tmp/hermes-chrome-debug.log | tail -40
```

Expected: JSON with `webSocketDebuggerUrl`, and the log often includes `DevTools listening on ws://127.0.0.1:9222/...`.

## Detect whether Hermes browser tools are still isolated

Use a unique marker URL in Hermes `browser_navigate`, then compare against the real Chrome tab list from CDP.

Marker example:
- `https://example.org/?hermes_retest=YYYYMMDDx`

If the marker URL does **not** show up in `http://127.0.0.1:9222/json/list`, Hermes browser tools are still isolated and not attached to the real Chrome.

This is the most reliable proof.

## Fallback: attach with Playwright over CDP

Use terminal + Playwright directly:

```bash
node <<'NODE'
const { chromium } = require('playwright');
(async() => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const contexts = browser.contexts();
  console.log('contexts', contexts.length);
  for (const [i, ctx] of contexts.entries()) {
    const pages = ctx.pages();
    console.log('context', i, 'pages', pages.length);
    for (const [j, p] of pages.entries()) {
      console.log('page', j, await p.title(), '|', p.url());
    }
  }
  await browser.close();
})();
NODE
```

If that succeeds, you are attached to the user's real Chrome.

## Prove control of the real browser

Navigate a unique URL via Playwright attach:

```bash
node <<'NODE'
const { chromium } = require('playwright');
(async() => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages()[0] || await ctx.newPage();
  await page.goto('https://example.net/?pw_attach=YYYYMMDDx', { waitUntil: 'load' });
  console.log(await page.title(), page.url());
  await browser.close();
})();
NODE
```

Then confirm it appears in the CDP tab list:

```bash
python - <<'PY'
import urllib.request, json
u='http://127.0.0.1:9222/json/list'
with urllib.request.urlopen(u, timeout=5) as r:
    data=json.load(r)
urls=[t.get('url','') for t in data if t.get('type')=='page']
for u in urls:
    print(u)
PY
```

If the unique URL appears there, you are controlling the real Chrome.

## Verify real login state

Open a logged-in site the user says is already authenticated, like Gmail:

```bash
node <<'NODE'
const { chromium } = require('playwright');
(async() => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const ctx = browser.contexts()[0];
  const page = await ctx.newPage();
  await page.goto('https://mail.google.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);
  console.log('TITLE', await page.title());
  console.log('URL', page.url());
  const body = await page.locator('body').innerText().catch(() => '');
  console.log(body.slice(0, 800).replace(/\s+/g, ' ').trim());
  await browser.close();
})();
NODE
```

Interpretation:
- If you land in inbox, you are using the real logged-in browser session
- If you land on a sign-in page, you are still not using the real session

Important Slack-specific nuance:
- A real-CDP-attached Chrome can be logged into one service and still be unauthenticated for Slack admin surfaces
- In practice, Gmail may open authenticated while `https://api.slack.com/apps` still shows a sign-in prompt and `https://bosswu.slack.com/` still lands on Slack login
- Do not treat that as proof that CDP attach failed
- It means the debug Chrome profile does not currently have Slack admin auth, even though the browser bridge is real
- When this happens, use live Slack API checks, Slack MCP history reads, and Hermes gateway behavior to diagnose Slack backend issues instead of blocking on Slack admin UI access

## macOS-specific finding: gstack browse may be blocked

On Brian's macOS machine, this failed:
- `~/.claude/skills/gstack/browse/dist/browse status`
- `~/.claude/skills/gstack/browse/dist/browse --help`

Symptoms:
- `Killed: 9`
- exit code 137
- `spctl --assess --type execute` reports signature problems
- `log show` shows `syspolicyd` / Gatekeeper-related events

If you see that pattern, stop trying to force gstack browse first. Switch to the direct Chrome CDP fallback above.

## Decision rule

Use this order:
1. Hermes `/browser connect` if you are inside Hermes CLI and can set `BROWSER_CDP_URL`
2. If that session still behaves isolated, prove it with the unique-marker URL test
3. Then switch to terminal + Playwright `connectOverCDP('http://127.0.0.1:9222')`
4. Use the real attached browser for the actual task

## GitHub maintainer-gate verification pattern

When the user wants you to clear a GitHub Actions approval gate for a fork PR, do not stop at PR summary text like `action_required`.
Use the real attached Chrome and verify the actual maintainer controls.

Recommended flow:
1. Open the PR page in the real Chrome session.
2. Open the PR checks page.
3. Open one concrete workflow run page.
4. Verify both:
   - the page text says something like `This workflow is awaiting approval from a maintainer`
   - whether any real control is rendered, such as:
     - `Approve and run`
     - `Approve workflows to run`
     - `Run workflow`
     - `Run jobs`

Important interpretation rule:
- If the page clearly says approval is required BUT none of those buttons exist in the real logged-in session, the current GitHub account does not have the maintainer-level permission needed to clear the gate.
- That is a permissions conclusion, not a browser-failure conclusion.

This matters because the user may already be fully logged in, and the PR page may still be non-actionable from that account.
In that case, the correct next step is:
- switch the real Chrome session to a maintainer-capable GitHub account
- then retry the exact same run page and click the approval control

## Why this works

The core distinction is simple:
- isolated browser session: only the tool can see it
- CDP-attached real Chrome: the user and the tool are acting on the same browser, tabs, cookies, and login state

When the user says "I already logged in", prefer the second one.
