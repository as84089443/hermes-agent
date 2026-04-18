---
name: slack-mcp-boss-mode-control-layer
description: Connect Slack to Hermes through native MCP as a proactive control layer, then combine MCP write tools with Slack user-token history reads to build a usable boss-mode channel workflow even when bot mention events are still unreliable.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [slack, mcp, boss-mode, control-layer, gateway, fallback]
---

# Slack MCP Boss-Mode Control Layer

Use when:
- Slack bot DM works but channel `@bot` is still unreliable
- the user wants Slack to be usable now, not only after inbound events are fully repaired
- you need a proactive Slack read/write side channel for boss-mode control
- Hermes native MCP is available and you want Slack tools directly inside Hermes

## Core insight

Do not wait for the Slack bot mention path to be perfect before making Slack useful.

If inbound bot events are flaky, add a second lane:
1. keep fixing the normal Slack gateway/bot path
2. in parallel, attach a Slack MCP server so Hermes can proactively read and write Slack

This creates a practical fallback/control layer:
- MCP for proactive channel reads/writes
- normal gateway for eventual conversational bot behavior

## What this solves

This method gives the user a usable Slack operator surface even when:
- `app_mention` still does not trigger reliably
- event subscriptions are incomplete
- Slack admin UI is difficult to automate or save correctly
- bot scopes are only partially repaired

It does NOT automatically fix bot inbound events.
It gives you a second way to operate Slack right now.

## Prerequisites

- Hermes native MCP support available (`mcp` Python package installed)
- `npx` available
- valid Slack bot token already present in `~/.hermes/.env`
- Slack workspace/team id known
- optional but highly useful: Slack user OAuth token for history reads

## Recommended server

A working stdio Slack MCP server:
- `@zencoderai/slack-mcp-server`

Ad-hoc verification command:
```bash
source venv/bin/activate
python - <<'PY'
import os, subprocess
from hermes_constants import get_hermes_home
from hermes_cli.env_loader import load_hermes_dotenv
load_hermes_dotenv(hermes_home=get_hermes_home())
env = os.environ.copy()
env['SLACK_TEAM_ID'] = 'TXXXXXXXXXX'
cmd = [
    'mcporter', 'list',
    '--stdio', 'npx -y @zencoderai/slack-mcp-server --transport stdio',
    '--name', 'slack_bw',
    '--output', 'json'
]
proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
print(proc.stdout)
print(proc.stderr)
PY
```

Expected result:
- server comes up successfully
- tools like `slack_post_message`, `slack_reply_to_thread`, `slack_list_channels` appear

## Native MCP configuration

Write to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  slack_bw:
    command: npx
    args:
      - -y
      - '@zencoderai/slack-mcp-server'
      - --transport
      - stdio
    env:
      SLACK_BOT_TOKEN: xoxb-...
      SLACK_TEAM_ID: TXXXXXXXXXX
    timeout: 120
    connect_timeout: 60
    sampling:
      enabled: false
```

Notes:
- `env` is important because Hermes MCP subprocesses run with a filtered environment
- if `SLACK_TEAM_ID` is not present in `.env`, inject it explicitly in this config
- disable sampling unless you specifically need server-initiated LLM calls

## Verification after config

Run:
```bash
source venv/bin/activate
python - <<'PY'
from tools.mcp_tool import discover_mcp_tools
from tools.registry import registry

discover_mcp_tools()
for name in sorted(registry._tools):
    if name.startswith('mcp_slack_bw_'):
        print(name)
PY
```

Expected tools include:
- `mcp_slack_bw_slack_list_channels`
- `mcp_slack_bw_slack_post_message`
- `mcp_slack_bw_slack_reply_to_thread`
- `mcp_slack_bw_slack_get_channel_history`
- `mcp_slack_bw_slack_get_users`
- `mcp_slack_bw_slack_get_user_profile`

## Important real-world limitation

The MCP Slack server may still inherit the Slack bot token's scope limits.
A common pattern:
- `slack_post_message` works
- `slack_reply_to_thread` works
- `slack_list_channels` may partially work
- `slack_get_channel_history` fails with `missing_scope` because the bot still lacks `channels:history`

Do not misread this as MCP failure.
It is still useful as a write/control layer.

## High-value workaround: split reads and writes

If the Slack bot token still lacks history scopes:
- use Slack MCP / bot token for writes
- use `SLACK_USER_OAUTH_TOKEN` for history reads via direct Slack Web API

This hybrid pattern is extremely practical.

### Read channels via user token
```bash
source venv/bin/activate
python - <<'PY'
import os, json, urllib.request, urllib.parse
from hermes_constants import get_hermes_home
from hermes_cli.env_loader import load_hermes_dotenv
load_hermes_dotenv(hermes_home=get_hermes_home())
user=os.getenv('SLACK_USER_OAUTH_TOKEN','').strip()
params=urllib.parse.urlencode({'types':'public_channel','exclude_archived':'true','limit':'50'})
req=urllib.request.Request('https://slack.com/api/conversations.list?' + params, headers={'Authorization': f'Bearer {user}'})
with urllib.request.urlopen(req, timeout=20) as resp:
    print(resp.read().decode())
PY
```

### Read channel history via user token
```bash
source venv/bin/activate
python - <<'PY'
import os, json, urllib.request, urllib.parse
from hermes_constants import get_hermes_home
from hermes_cli.env_loader import load_hermes_dotenv
load_hermes_dotenv(hermes_home=get_hermes_home())
user=os.getenv('SLACK_USER_OAUTH_TOKEN','').strip()
params=urllib.parse.urlencode({'channel':'CXXXXXXXXXX','limit':'8'})
req=urllib.request.Request('https://slack.com/api/conversations.history?' + params, headers={'Authorization': f'Bearer {user}'})
with urllib.request.urlopen(req, timeout=20) as resp:
    print(resp.read().decode())
PY
```

### Write message via MCP
```bash
mcporter call --stdio "npx -y @zencoderai/slack-mcp-server --transport stdio" slack_post_message channel_id=CXXXXXXXXXX text='結論：... 現況：... 下一步：...' --output json
```

## Boss-mode control-layer pattern

Build a thin local script that does three jobs:
1. list readable channels
2. summarize recent channel history into boss-mode language
3. post / reply through Slack MCP

Recommended CLI surface:
- `channels`
- `summary <channel>`
- `post <channel> <text>`
- `reply <channel> <thread_ts> <text>`

Then evolve it one step further into a fixed control-channel mode so the user does not need to repeat the channel name every time.

Recommended additional commands:
- `set-default <channel>` — choose the permanent boss-mode control channel
- `show-default` — show the current default channel
- `control-status` — produce a boss-mode digest for the default channel
- `default-post <text>` — post directly into the default channel
- `default-reply <thread_ts> <text>` — reply directly in the default channel thread
- `watch-once` — scan the default channel for a new top-level user task and open a thread kickoff
- `watch-loop --interval <seconds>` — continuously poll the default channel and auto-open thread kickoffs

Recommended state file:
- `get_hermes_home() / "slack_mcp_boss_mode.json"`

Store at least:
- `default_channel`
- `default_channel_id`

Implementation pattern:
- persist state under `get_hermes_home()` (for example `~/.hermes/slack_mcp_boss_mode.json`)
- save both `default_channel` and `default_channel_id`
- let `control-status` summarize the latest actionable items in the fixed channel, not just generic recent messages
- for Phase 1, treat each new top-level user message in the control channel as a task candidate
- use `watch-once` to detect the newest unprocessed top-level user message, skip thread replies, and auto-reply in-thread with a kickoff message
- do NOT blindly skip every message with `bot_id`; real user-authored messages sent via some Slack paths can still carry a `bot_id`. Only ignore Hermes' own known bot identity (`BOT_USER_ID` / `BOT_ID`).
- use `watch-loop` as the operational fallback when Slack inbound events are still unreliable; it can poll every N seconds and call the same `watch-once` logic repeatedly
- keep a `processed_top_level_ts` list per channel in the state file to avoid duplicate thread kickoffs
- when calling `slack_reply_to_thread` through mcporter, pass `thread_ts` via `--args` JSON and cast it to a string first; plain `key=value` calls may be coerced to numbers and fail schema validation
- add an `active_from_ts` baseline per channel in the state file when `watch-loop`/`watch-once` first starts; without this, the watcher may replay old backlog messages and open thread lanes for historical test chatter instead of only new tasks
- on first start, set `active_from_ts` and `last_seen_ts` to the newest currently visible message, then only process messages with `ts > active_from_ts`
- if you replace an old watcher with a new version, kill the old background process explicitly and reset the state baseline before trusting the new loop's behavior
- add a separate watcher singleton state file (for example `~/.hermes/slack_mcp_watcher_state.json`) that records the active watcher pid, channel, start time, and log path
- expose a `watcher-status` command so you can verify the true active watcher instead of trusting delayed platform notifications about old background jobs exiting
- also expose `ensure-watcher`, which should do two jobs in one command: if no watcher is running, start one; if one is already healthy, return `already_running` with the real pid, channel, and log path so the operator can trust the current watcher immediately
- treat `ensure-watcher` as the operator-facing truth source after noisy background wrapper exits; it is more useful than asking the user to manually interpret process notifications
- delayed background completion notifications from earlier watcher shells are normal; rely on `watcher-status`, `ensure-watcher`, the singleton state file, and the current log file as the source of truth
- `watcher-status` should also surface all live watch-loop python pids, not only the tracked pid; otherwise stale untracked loops can continue processing new tasks while the state file claims everything is singleton-safe
- add `cleanup-stale-watchers` to terminate any watch-loop pids that are not the tracked singleton pid before trusting new behavior or validating a routing fix
- if you change watcher logic in `slack_mcp_boss_mode.py`, restart the running watcher process; otherwise a healthy old pid may continue serving stale behavior from old code and make the system look partially broken
- after a new lane is created, immediately persist a lane registry entry containing at least: `lane_id`, `source_ts`, `thread_ts`, `kickoff_ts`, `status`, and timestamps
- before any Slack side effects for a new top-level task, atomically claim that `source_ts` in state (for example `in_flight_top_level_ts`) so concurrent watcher passes cannot open duplicate thread lanes for the same message
- only mark a top-level task processed after the lane path finishes successfully; if kickoff or downstream execution fails, release the in-flight claim so the task can be retried cleanly
- do NOT stop at top-level kickoff detection only; also scan replies inside active thread lanes and treat user thread replies as follow-up turns on the same lane
- store the Hermes child `session_id` on the lane after the first agent reply, then when a user continues the same thread, resume with `hermes chat --resume <session_id>` instead of starting a fresh session every time
- keep separate lane fields for reply continuity, for example `last_seen_thread_reply_ts` / `last_user_reply_ts`, so the watcher can detect only new human thread replies and avoid reprocessing old bot messages
- for thread readability, avoid a rigid three-heading template on every reply. Use a half-structured style: first line explicitly acknowledges the user's latest thought, then 1–3 short natural paragraphs about current understanding and next move. Reserve heavier boss-mode headings for real decisions / blockers / closeout only
- in practice, a better lane cadence was: one short kickoff reply, one short "I’m taking this direction" reply, then the substantive agent result. Removing extra "entered execution" filler messages made the thread feel more like an ongoing terminal conversation and less like a workflow bot
- in `run_queue_once`, clear `queue.active` in a `finally` block and catch `SystemExit`/other non-Exception failures from `execute_lane`; otherwise one bad lane can wedge the worker forever
- add `reconcile-stale-lanes` to mark long-idle nonterminal lanes as `stale`, and surface `stale_lane_count` in `queue-status` so operators can tell live work from abandoned residue
- add explicit governance commands like `block-lane`, `complete-lane`, and `close-lane` that both update lane status and post a readable thread summary, so lane lifecycle can move beyond `agent_replied` into operator-visible closeout states
- when the lane is a normal real task, do NOT spam the thread with multiple near-duplicate status blurbs like `kickoff`, `已開始處理`, `已進入執行` in rapid succession — this makes the thread feel like it only got an initial canned response instead of real follow-through
- better pacing for boss-mode readability is:
  1. one short kickoff reply in-thread
  2. one short `已開始處理` progress reply
  3. the first real execution result / plan / deliverable reply
- keep kickoff/status pacing sparse; do NOT stack multiple near-duplicate thread replies like `kickoff`, `已開始處理`, `已進入執行` unless each one adds real state change
- latest user preference is stricter than the earlier sparse model: for normal work lanes, do NOT emit kickoff boilerplate in the thread and do NOT emit parent-channel `已接手 / 現況 / 下一步` summaries at all; after the user posts, the next visible assistant message should be the first real content-bearing reply
- a practical v2 upgrade is to add `execute-lane <lane_id>` that runs a non-interactive Hermes child session (`hermes chat -Q -q ... --source tool`) and posts the result back into the lane thread
- important continuity upgrade: when the user replies inside the existing Slack thread, treat that as the same work lane instead of only watching new top-level posts
- persist the Hermes `session_id` on the lane record after the first agent reply, then on later thread replies call Hermes with `--resume <session_id>` so the thread feels like one continuing conversation rather than repeated fresh kickoffs
- when posting the child-session result back into Slack, strip helper metadata like trailing `session_id: ...` lines so the thread stays user-facing
- detection order should be: first check for new user replies in existing nonterminal lanes, then check for brand-new top-level tasks
- for thread-reply continuation, track at least `last_seen_thread_reply_ts` per lane so the watcher does not reprocess old replies
- prompt continued thread replies to read like terminal/TG conversation: short paragraphs, explicit acknowledgement of the user's latest thought, and no rigid `結論 / 現況 / 下一步` headings unless they materially help readability
- after that, move from direct immediate execution to an explicit `execution_queue` with `pending`, `active`, and `history`, plus `queue-status` and `run-queue-once` commands, so lane execution can evolve into a worker model instead of ad-hoc direct calls

Recommended summary shape:
- 結論
- 現況
- 下一步
- 關鍵片段

This gives the user a usable Slack operator interface immediately, and the fixed control-channel mode turns it into a repeatable daily command surface.

## Reusable artifact pattern

A useful implementation is a local helper such as:
- `scripts/slack_mcp_boss_mode.py`

Suggested behavior:
- load `SLACK_BOT_TOKEN` and `SLACK_USER_OAUTH_TOKEN`
- use user token for `conversations.list` and `conversations.history`
- use MCP / bot token for `post` and `reply`
- translate recent messages into decision-oriented Traditional Chinese summaries

## Additional real-world findings

### Merge-conflict blocker can break the helper before Slack logic even runs
If the helper imports Hermes config/env loading utilities and suddenly fails with a `SyntaxError`, inspect Hermes source for leftover merge-conflict markers before debugging Slack itself.

Observed example:
- `hermes_cli/config.py` contained `<<<<<<<` / `=======` / `>>>>>>>`
- this broke `load_hermes_dotenv()` transitively
- the Slack MCP helper looked broken, but the real issue was unrelated repo state

Practical rule:
- if a helper that previously worked now dies during startup, run `python -m py_compile` on the helper and any imported Hermes config modules first
- fix repo syntax breakage before touching Slack auth or MCP config

### Fixed control channel is the right operator abstraction
In practice, once reads and writes are working, the highest-value next step is not more generic tool coverage.
It is choosing one default Slack channel and treating it as the operator control lane.

Observed good default:
- a public channel like `#一般` can become the stable boss-mode control lane
- the helper should be able to emit a `control-status` digest and post directly into that lane without requiring the channel name every time

### Free-response channel config is worth setting during control-channel rollout
If the control channel is intended to be the user's front desk, set it in Hermes config as a Slack free-response channel even before native inbound events are fully reliable.

Reusable pattern:
```yaml
slack:
  require_mention: true
  allow_bots: false
  free_response_channels: C0ACCPYAGVC
```

Why:
- once inbound events are fixed, the control channel should already behave like a direct command surface
- this removes the extra `@mention` requirement from the final UX
- it aligns the fallback MCP path and the eventual normal gateway path around the same channel

## Pitfalls

- assuming MCP fixes bot inbound event routing
- assuming channel history will work through MCP if the bot lacks `channels:history`
- forgetting that Hermes MCP subprocesses do not inherit all env vars by default
- forgetting to set `SLACK_TEAM_ID`
- trying to solve everything in Slack admin UI before giving the user a usable fallback lane

## Best use

Use this as a pragmatic second lane:
- bot/gateway path is the long-term conversational front door
- Slack MCP control layer is the immediate operator back door

That combination is often enough to make Slack usable during cutover, instead of blocking on perfect event behavior first.
