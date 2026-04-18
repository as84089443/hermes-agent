---
name: hermes-slack-cutover-and-token-mapping
description: Safely connect Slack to Hermes, correct common token mislabeling from older setups, verify live auth, and distinguish local cutover from Slack-side app identity cleanup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [slack, hermes, gateway, migration, token-mapping, openclaw]
---

# Hermes Slack Cutover and Token Mapping

Use when:
- connecting Slack to Hermes gateway
- migrating from OpenClaw or another older setup
- the user provides Slack credentials in a pasted bundle
- the pasted labels may be wrong or inherited from another system

## Critical token mapping rule

Hermes Slack adapter expects:
- `SLACK_BOT_TOKEN` = `xoxb-...`
- `SLACK_APP_TOKEN` = `xapp-...`

Common migration failure:
- users or old notes label these backwards
- if the values are swapped, Hermes will appear configured but Slack connection will fail or behave oddly

Do not trust the human-written label blindly.
Trust the token prefix.

## Additional optional Slack env vars often provided

These are not required for Hermes Socket Mode connection, but may still be worth storing for future use:
- `SLACK_USER_OAUTH_TOKEN` = `xoxp-...`
- `SLACK_CLIENT_ID`
- `SLACK_CLIENT_SECRET`
- `SLACK_SIGNING_SECRET`
- `SLACK_VERIFICATION_TOKEN`

## Hermes runtime expectations

Relevant Hermes behavior discovered from code:
- `gateway/platforms/slack.py` requires:
  - `SLACK_BOT_TOKEN`
  - `SLACK_APP_TOKEN`
- Slack runs via Socket Mode using `slack-bolt`
- Hermes acquires a scoped platform lock on the Slack app token, so a second process will fail to connect while another gateway instance is already using it

## Safe cutover workflow

### 1. Inspect existing config first

Check:
- `~/.hermes/.env`
- project-local env if applicable (for example app integrations)
- whether older OpenClaw-era values already exist

Look specifically for:
- swapped `xoxb` / `xapp` assignments
- partial tokens already stored
- stale OpenClaw naming assumptions

### 2. Write corrected values to Hermes env

At minimum update:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

If supplied, also store:
- `SLACK_USER_OAUTH_TOKEN`
- `SLACK_CLIENT_ID`
- `SLACK_CLIENT_SECRET`
- `SLACK_SIGNING_SECRET`
- `SLACK_VERIFICATION_TOKEN`

### 3. Verify each credential live against Slack API

Use network verification, not assumptions.

Recommended checks:

Bot token:
```python
POST https://slack.com/api/auth.test
Authorization: Bearer <xoxb token>
```
Expected:
- `ok: true`
- workspace and bot user returned

User OAuth token:
```python
POST https://slack.com/api/auth.test
Authorization: Bearer <xoxp token>
```
Expected:
- `ok: true`

App token:
```python
POST https://slack.com/api/apps.connections.open
Authorization: Bearer <xapp token>
```
Expected:
- `ok: true`
- response includes a WebSocket `url`

## Important interpretation rule

If `auth.test` succeeds for the bot token and `apps.connections.open` succeeds for the app token, the credentials are valid even if Hermes has not yet shown Slack activity in the logs.

## 4. Verify Hermes dependencies and gateway state

Check:
- `slack-bolt` import works
- `slack_sdk` import works
- `hermes status` reports Slack configured
- restart gateway after env updates

Typical commands:
```bash
source venv/bin/activate
python -c "import slack_bolt, slack_sdk; print('slack_deps_ok')"
hermes status
hermes gateway restart
hermes gateway status
```

## 5. Handle lock conflicts correctly

If a manual connection test says the Slack app token is already in use by another PID:
- do not treat that as auth failure
- check the running gateway process
- this usually means the installed Hermes gateway service already owns the token

This is expected behavior due to the scoped platform lock.

## 5.5 Authorization allowlist can block a seemingly-valid cutover

A fully valid Slack connection can still look "dead" to the user if Hermes authorizes nobody.

Observed reusable pattern:
- `hermes status` can show Slack configured
- bot/user/app tokens can all pass live auth checks
- bot can even send outbound DMs successfully
- but inbound user messages are still silently denied because no allowlist is configured

Check these env vars explicitly:
- `SLACK_ALLOWED_USERS`
- `SLACK_ALLOW_ALL_USERS`
- `GATEWAY_ALLOW_ALL_USERS`

Practical safe move for a controlled cutover:
- add the target operator's Slack user ID to `SLACK_ALLOWED_USERS`
- restart the gateway
- then validate inbound from that user first

Do not assume outbound success means inbound authorization is working.

## 5.6 Validate in this order: auth -> outbound DM -> inbound DM -> channel mention

For real Slack cutovers, use this exact verification sequence:

1. `auth.test` on bot token
2. `apps.connections.open` on app token
3. `auth.test` on user OAuth token if available
4. send a bot-authored DM to the target operator
5. have the operator reply in DM
6. only after DM works, test channel usage with:
   - bot invited into the channel
   - explicit `@botname` mention

Why this matters:
- DM success proves workspace identity + bot posting + user targeting
- DM reply is the cleanest inbound-path test
- channel failures after DM success usually mean channel presence, scopes, or event subscription problems — not token problems

## 6. Check the app's effective scopes against Hermes adapter behavior

A Slack bot can be fully authenticated and still appear "dead" to the user if Hermes denies incoming messages due to authorization policy.

Important finding:
- Hermes gateway warns when no allowlists are configured
- in that state, unauthorized users are denied by default
- for Slack, a practical fix is to set either:
  - `SLACK_ALLOWED_USERS=<slack_user_id>`
  - or a broader allow-all setting if that is intentional

Practical workflow:
1. resolve the human operator's Slack user ID using `auth.test` on their user token (`xoxp-...`)
2. write that ID into `SLACK_ALLOWED_USERS`
3. restart the gateway
4. only then test inbound messages from that user

Without this step, outbound bot messages may work while inbound user→Hermes conversation still fails.

## 5.6 Use direct DM delivery as a first live-presence check

When the user says "I still can't see you in Slack," do not start by testing complex channel flows.
First prove simple bot presence with a direct DM.

Reusable pattern:
1. use `auth.test` on `SLACK_USER_OAUTH_TOKEN` to get the target user's `user_id`
2. call `chat.postMessage` with the bot token to that `user_id`
3. verify Slack returns `ok: true`, a DM channel id (`D...`), and a message timestamp
4. ask the user to reply in that DM with a simple word like `測試`

Why this is the best first check:
- confirms workspace identity is correct
- confirms bot can reach the actual user
- avoids channel membership ambiguity
- isolates the final blocker to inbound event handling if the user still cannot converse

## 6. Check the app's effective scopes against Hermes adapter behavior

Do not stop after token auth succeeds.
A valid token can still be under-scoped for Hermes' actual Slack features.

### Hermes Slack adapter capabilities observed in code
From `gateway/platforms/slack.py`, Hermes uses or may use these Slack APIs:
- `chat_postMessage`
- `chat_update`
- `assistant_threads_setStatus`
- `conversations_info`
- `conversations_replies`
- `users_info`
- `files_upload_v2`
- `reactions_add`
- `reactions_remove`
- slash command `/hermes`
- Block Kit interactive button actions for approvals

### Practical scope audit pattern
After auth succeeds, probe likely-required APIs and record `missing_scope` responses.
Useful checks:
- `users.info` → validates `users:read`
- `conversations.history` on a public channel → validates `channels:history`
- `reactions.add` → validates `reactions:write`
- `conversations.list types=public_channel,private_channel,im,mpim` → exposes `groups:read` / DM read gaps

### Real-world scope findings worth remembering
A Slack app may already have enough scopes for basic Hermes posting while still missing key behavior for full operator UX.
In one successful cutover, auth passed but the following scopes were still missing:
- `users:read`
- `groups:read`
- `channels:history`
- `reactions:write`

### Recommended bot scopes for a full Hermes Slack setup
Use this as the canonical target set when preparing or repairing the Slack app:
- `app_mentions:read`
- `assistant:write`
- `channels:history`
- `channels:read`
- `chat:write`
- `chat:write.public`
- `commands`
- `files:read`
- `files:write`
- `groups:history`
- `groups:read`
- `im:history`
- `im:read`
- `mpim:history`
- `mpim:read`
- `reactions:write`
- `users:read`

### Required Slack-side features
For Hermes' current Slack integration, ensure the app also has:
- Socket Mode enabled
- Interactivity enabled
- slash command `/hermes`
- bot events:
  - `app_mention`
  - `assistant_thread_started`
  - `assistant_thread_context_changed`
  - `message.channels`
  - `message.groups`
  - `message.im`
  - `message.mpim`

### Reusable artifact pattern
When doing a serious cutover, generate a reusable manifest/spec file for the user to import or compare in Slack App settings.
Good output paths:
- `docs/specs/slack-hermes-boss-mode-manifest.yaml`
- `docs/plans/<date>-slack-cutover-boss-mode.md`

## 6.5 Add conservative gateway defaults for Slack before opening it up

Recommended initial Hermes config:
- `slack.require_mention: true`
- `slack.allow_bots: false`
- `slack.free_response_channels: ''`

Why:
- mention-gating prevents noisy over-replies in channels
- bot-to-bot traffic is usually low-value noise during cutover
- free-response channels should only be opened intentionally after validation

## 6.6 Boss-mode formatting is part of the cutover, not an optional polish step

If the user wants Slack to be a leadership / operator interface, do not leave Hermes in generic chatty mode.
Patch the Slack platform guidance so Slack replies default to:
- Traditional Chinese
- short conclusion first
- current status second
- next decision / next action third
- minimal raw IDs / internal enums / engineering jargon unless necessary

Preferred decision/update shape:
- 結論
- 現況
- 你現在要決定什麼
- 批准後會發生什麼
- 若不同意會退回哪裡
- 下一步

A practical place to inject this behavior is the Slack-specific platform note inside `gateway/session.py`.

## 6.7 Thread-first operating model is the real multi-session UX

If the user wants to manage many concurrent workstreams from Slack, do not treat Slack as one flat channel transcript.
Use a thread-first operating model:
- main channel = command / summary / decisions
- one Slack thread = one work lane / one shared session
- detailed execution stays in-thread
- only surface boss-mode summaries back to the parent channel for:
  - new lane kickoff
  - blocker needing attention
  - approval / decision request
  - closeout / result worth surfacing

Implementation notes:
- preserve Slack `thread_ts` when building Hermes session source/context
- avoid silently forcing slash commands into DM-like context when they were launched from a channel thread
- keep top-level channel kickoff replies short (`結論 / 現況 / 下一步`) and continue the real work inside the thread
- for top-level channel kickoff messages, prefer a dual-layer routing model:
  - parent channel gets a short boss-mode summary only
  - detailed execution reply stays in the Slack thread
- a safe first implementation is metadata-driven routing (for example a `slack_parent_summary` flag) that lets the Slack adapter emit one short parent summary before the full threaded reply

This is the practical path to “multi-session development in Slack” without turning Slack into an unreadable log firehose.

## 6.8 Outbound DM success narrows the failure domain

If the Slack bot can successfully send a direct message to the user, then these are already proven:
- bot token is valid
- app token is valid enough for Socket Mode startup
- the workspace mapping is correct
- Hermes can reach the Slack Web API

At that point, if the user still says "I can't talk back to it" or channel mentions do nothing, stop blaming Hermes broadly.
The remaining problem is usually one of:
- App Home / Messages Tab disabled
- missing channel/event scopes
- bot not present in the target channel
- Slack-side event subscription gaps

This is an important diagnostic shortcut: outbound DM success means the integration is partially live, and the remaining blocker is usually Slack app configuration, not token correctness.

## 6.9 Specific Slack blocker: “已關閉傳送訊息到此應用程式”

If the user can see the bot's DM but Slack shows:
- `已關閉傳送訊息到此應用程式`

then the likely root cause is Slack App Home configuration, not Hermes routing.

Tell the user to open the Slack app settings and enable:
- `App Home`
- `Messages Tab`
- `Allow users to send Slash commands and messages from the messages tab`

Why this matters:
- without App Home messaging enabled, Slack allows the app to send outbound messages
- but blocks the user from replying in the app DM surface
- this creates the misleading symptom "the bot can message me, but I can't message it back"

After enabling those settings, test DM inbound first before debugging channel mentions.

## 6.8 Live cutover findings from a real BW workspace

A real Slack cutover uncovered a few high-value operational truths:

### Outbound can work before inbound is truly usable
You may verify all of these successfully:
- `auth.test` for bot token
- `apps.connections.open` for app token
- gateway restart succeeds
- bot can proactively send a DM to the target user

And still not have a usable operator experience.

Why:
- DM replies can still be blocked by Slack App Home settings
- channel mentions can still fail because scopes / event subscriptions / channel presence are incomplete

So do not treat "bot successfully sent me a DM" as final cutover success.
It only proves outbound delivery.

### Slack message tab can silently block DM replies
A concrete failure mode:
- user sees the bot's DM
- but Slack shows: `已關閉傳送訊息到此應用程式`

This means the Slack app's App Home messaging path is disabled.

Required Slack-side fix:
- Slack App settings → `App Home`
- enable `Messages Tab`
- enable `Allow users to send Slash commands and messages from the messages tab`

Until this is enabled, DM inbound testing is invalid even if outbound DM works.

### Channel silence after invite + mention is usually not a token bug
If the user says:
- they invited the bot into a channel
- they @mentioned it
- nothing happened

Do NOT jump to "token broken."
More likely causes:
- bot lacks channel scopes
- bot event subscriptions are incomplete
- bot is not actually present/usable in that channel despite invite
- mention gating is on and the event stream never reaches Hermes

Important stronger diagnostic learned in practice:
- after expanding scopes and reinstalling the app, verify bot capabilities directly with Web API calls like:
  - `conversations.list`
  - `users.info`
  - `reactions.add`
- if those now return `ok: true`, then missing scope is no longer the main suspect
- next, temporarily disable any polling fallback/watcher path and send a fresh channel `@mention` test
- if there is still no reply and no corresponding event shows up in Hermes logs, the remaining blocker is very likely Slack-side Event Subscriptions not actually persisting
- in other words: if scopes are good and watcher is off, but native inbound still never arrives, stop changing Hermes code and focus on fixing Slack admin event delivery

Also check Hermes adapter behavior directly:
- if `gateway/platforms/slack.py` registers `app_mention` as a no-op and relies only on `message` events, then channel `@bot` can stay silent whenever Slack is delivering `app_mention` but not `message.channels`
- practical fix: route `app_mention` into `_handle_slack_message(event)` instead of `pass`
- then add/keep a regression test proving the registered `app_mention` handler actually awaits `_handle_slack_message`
- another real bug found during live cutover: some Slack App Home / assistant / user-token-authored events can carry a `bot_id` even though they were written by a human, and some DM events may lack `user` while assistant thread metadata still contains the real user id
- practical fix: in `gateway/platforms/slack.py`, resolve assistant thread metadata BEFORE bot-message filtering, treat events with a human `user` (or assistant-metadata `user_id`) as human-authored even if `bot_id` is present, and only blanket-ignore true bot messages (`subtype == 'bot_message'` or `bot_id` with no human identity)
- keep regression tests for both cases:
  - human-authored DM with `bot_id` should still reach `handle_message`
  - assistant-thread DM without `user` but with cached assistant metadata should still reach `handle_message`

This is a high-value fallback because Slack admin UI can make `message.channels` hard to enable reliably during live cutovers.

### Missing scope diagnostics worth checking immediately
In the BW cutover, these API calls failed with `missing_scope` even though auth worked:
- `conversations.list`
- `users.info`
- `bots.info`

This is a strong signal the app is under-scoped for channel-oriented operation.

### Minimal DM-first / channel-second verification order
Use this order every time:

1. Verify workspace binding
- `auth.test` for bot token should return the expected workspace name and team_id

2. Verify outbound DM
- send a bot-authenticated DM to the target user

3. Verify DM inbound
- user replies in App Home / DM
- if Slack blocks replies, fix `App Home` first

4. Verify channel inbound
- ensure bot is invited
- test explicit `@bot` mention
- only then investigate thread-first channel behavior

This order avoids wasting time debugging channel behavior when App Home or scopes are still broken.

### Allowlist can block real users even when Slack is configured
Gateway warning observed:
- no allowlists configured
- unauthorized users will be denied

For Slack, make sure either:
- `SLACK_ALLOWED_USERS` contains the target Slack user ID, or
- a broader allow-all strategy is intentionally enabled

A practical pattern is:
- derive the user ID from `SLACK_USER_OAUTH_TOKEN` via `auth.test`
- write that user ID to `SLACK_ALLOWED_USERS`
- restart the gateway

### Slack reply cleanup: strip self-mentions from outgoing boss-mode summaries

Observed real-world annoyance:
- even after renaming the Slack app to `Hermes Agent`, replies could still visibly show `OpenClaw_Assistant`
- the cause was not only sender identity — Hermes sometimes echoed the triggering mention back into summaries, for example:
  - `交辦摘要：<@U_BOT>`
- Slack then rendered that mention using the bot user's stale legacy profile name, surfacing `OpenClaw_Assistant` inside the reply text itself

Practical fix in Hermes:
- sanitize outgoing Slack text before formatting/sending
- strip self-mentions for the adapter's own bot user IDs from:
  - normal sends
  - edits
  - parent-channel boss-mode summaries

Why this matters:
- it prevents stale OpenClaw-era naming from being reintroduced by reply content even when the visible sender/app name is already correct
- it is a clean mitigation even if Slack's underlying bot-user `real_name` cannot currently be changed

### Slack quiet-mode hardening for boss-mode channels

Observed product issue:
- Slack felt noisy because two independent mechanisms could still speak mid-turn:
  1. tool progress lines
  2. interim assistant commentary

Reusable operator-facing config:
```yaml
display:
  platforms:
    slack:
      tool_progress: off
      interim_assistant_messages: false
```

Important implementation finding:
- `interim_assistant_messages` must be resolved through the same per-platform display resolver as `tool_progress`
- if gateway code reads only `display.interim_assistant_messages` globally, the Slack-specific override is ignored and Slack remains noisy even though config looks correct

Verification pattern:
- add a platform-specific test proving `display.platforms.slack.interim_assistant_messages: false` suppresses commentary for Slack while leaving global/default behavior unchanged elsewhere
- restart the gateway after changing the display config

### MCP fallback is worth wiring in even before inbound events are fixed
If Slack bot inbound remains flaky, add a second control path via MCP instead of waiting on mention/event fixes.

Reusable pattern that worked:
1. Confirm Hermes native MCP is available:
   - `python - <<'PY' ... import mcp ...`
   - `mcporter list --output json`
2. Configure `~/.hermes/config.yaml` with a native MCP server:
   ```yaml
   mcp_servers:
     slack_bw:
       command: npx
       args: ["-y", "@zencoderai/slack-mcp-server", "--transport", "stdio"]
       env:
         SLACK_BOT_TOKEN: <existing xoxb token>
         SLACK_TEAM_ID: T0AC8E2D5DH
       timeout: 120
       connect_timeout: 60
       sampling:
         enabled: false
   ```
3. Restart Hermes so native MCP discovery runs again.
4. Verify tool discovery, for example by checking that tools like these appear:
   - `mcp_slack_bw_slack_post_message`
   - `mcp_slack_bw_slack_reply_to_thread`
   - `mcp_slack_bw_slack_get_channel_history`
   - `mcp_slack_bw_slack_list_channels`
5. Also verify ad-hoc with mcporter before trusting it:
   - `mcporter list --stdio "npx -y @zencoderai/slack-mcp-server --transport stdio" --name slack_bw --output json`
   - `mcporter call --stdio "npx -y @zencoderai/slack-mcp-server --transport stdio" slack_post_message channel_id=D... text='test' --output json`

What this buys you:
- Hermes can proactively read and write Slack via MCP even if bot mention events are still broken
- this is a stable operator backdoor for boss-mode control, thread replies, history reads, and directed outbound actions

Important limitation:
- Slack MCP does NOT replace the Slack gateway inbound event path
- it solves active operations (`read`, `post`, `reply`, `inspect history`), not passive `@Hermes` auto-response in channels
- treat it as a second Slack lane, not proof that mention subscriptions are fixed

A reusable escalation path on macOS is:
1. detect whether the user's real `Google Chrome` is running
2. use `osascript` to inspect open tab URLs and find the already-authenticated Slack app/admin tab
3. navigate that real Chrome tab directly to the needed Slack settings pages, for example:
   - `https://api.slack.com/apps/<APP_ID>/app-home`
   - `https://api.slack.com/apps/<APP_ID>/event-subscriptions`
   - `https://api.slack.com/apps/<APP_ID>/oauth?`
4. execute DOM JavaScript via AppleScript to click toggles, buttons, or read state text
5. verify the visible page state after each change instead of assuming the click worked

Why this matters:
- real Chrome already has the user's authenticated Slack admin session
- this bypasses the unreliable step of transferring login state into an isolated automation browser
- for Slack admin work, AppleScript + real Chrome can succeed where cookie import does not

Observed reusable findings:
- importing `.slack.com` cookies into an automation browser can report success yet still fail to unlock the workspace admin surface
- importing workspace-specific cookies such as `bosswu.slack.com` may yield zero imported cookies
- the cookie picker can fail with `Failed to fetch` when the local picker/browse session is stale; refreshing the browse session may recover the picker, but this still does not guarantee authenticated Slack admin access
- on macOS, direct AppleScript control of real Chrome was the first reliable method that actually changed Slack App settings in-place
- when the Slack admin UI shows `You’ve changed the permission scopes your app uses. Please reinstall your app for these changes to take effect`, do not treat that banner as informational only — the reinstall is a real gating step
- a practical way to finish that step is to navigate real Chrome to the app's `install-on-team` / OAuth authorize URL and click the localized `允許` / `Allow` button, then verify you land on `install-on-team?success=1`
- after this reinstall, immediately restart `hermes gateway` so Socket Mode reconnects with the updated installation context before asking the user to test again

Concrete Slack settings successfully changed with this approach:
- App Home: `Allow users to send Slash commands and messages from the messages tab`
- Event Subscriptions: `Enable Events`

Important limitation:
- adding bot events in Slack's Event Subscriptions UI may not persist cleanly through naive DOM scripting
- after scope changes, Slack may require `Reinstall to Workspace` before the UI truly commits the new behavior
- if the page still says `No events added yet` after scripted adds, treat it as an incomplete Slack-side save/reinstall problem, not proof that the browser-control method failed
- in live Chrome automation, do NOT keep opening new Slack admin tabs for every check; reuse the same `event-subscriptions` / `oauth` tab so you don't bury the operator under duplicate tabs and lose page state between actions
- the Event Subscriptions page uses Slack's `TSLazyFilterSelect` widget, not a plain visible `<select>`; reliable scripted adds come from the page context, for example:
  - get the widget with `jQuery('#add_bot_event').data('TSLazyFilterSelect')`
  - call `setValue('<event_name>')`
  - then click `#add_bot_event_btn`
- plain Playwright `selectOption()` / `fill()` against the hidden widget often fails because the control is intentionally invisible and virtualized
- after a scripted add, the body text can still misleadingly say `Subscribe to bot events` with no visible rows, while `#bot_events_table` HTML already contains the new event rows; inspect the table DOM directly, not only `document.body.innerText`
- the strongest save-failure indicator is the alert banner: `Oh no! We couldn't save the event subscriptions for this app.` Treat that as authoritative even if a previous save briefly showed `Success!`

### Slack admin UI can partially persist Event Subscriptions while still showing a save failure

Observed failure mode during a live cutover:
- after adding the needed bot events, Slack's Event Subscriptions page could still show:
  - `Oh no! We couldn't save the event subscriptions for this app.`
  - `Oops, something went wrong`
- yet the event rows could still appear in the table after reload
- the page can become internally inconsistent, for example event rows exist while the toggle/error state still looks wrong

Practical rule:
- do not trust the Slack admin UI alone
- after any event-subscription edit, verify BOTH:
  1. the rows actually exist after reload
  2. live channel/DM mentions trigger Hermes after gateway restart
- if live mentions work, treat the admin-page error as a UI/save inconsistency, not automatically as a blocking integration failure

Recommended validation sequence after editing Event Subscriptions:
1. reload the page and confirm required rows are present
2. run `hermes gateway restart`
3. send a fresh `@Hermes Agent` test in the target channel
4. only keep debugging the admin UI if live inbound still fails

- `Reinstall to BW` on the OAuth page is a plain link to Slack OAuth authorize; clicking it and then `允許` can return you to the OAuth settings page without a loud success banner, so verify reinstall by checking live Slack behavior (or an explicit success redirect), not just by seeing the page bounce back
- Slack naming can remain split across multiple surfaces even after App Home rename succeeds:
  - `bots.info` may show the new bot/app name (for example `Hermes Agent`)
  - Slack message `bot_profile.name` may also show the new name
  - but `users.info` for the bot user can still keep an old `real_name` like `OpenClaw_Assistant`
- this split matters because echoed self-mentions like `<@U_BOT>` can render using the stale bot-user identity in some Slack surfaces, making it look like the rename failed even when sender identity is already updated
- practical verification pattern after renaming:
  - check `bots.info` for the active `bot_id`
  - check `users.info` for the active `user_id`
  - compare `bot.name`, `user.name`, and `user.real_name`
- important Hermes-side product fix discovered during this cutover:
  - strip self-mentions for the bot's own user IDs from outgoing Slack text before `format_message()` / `chat_postMessage()` / `chat_update()`
  - also sanitize `_thread_parent_summary()` output the same way
  - otherwise summaries like `交辦摘要：<@U_BOT>` can surface the stale `OpenClaw_Assistant` name inside the reply body even after the visible app name was changed
- good regression test: sending `交辦摘要：<@U_BOT>` should produce posted Slack text with no `<@U_BOT>` left in the outgoing payload
This is usually faster than fighting Slack auth state transfer.

## 7. Distinguish local cutover from Slack-side branding cleanup

Very important migration finding:
- even after Hermes is correctly configured, `auth.test` may still return a bot username like `openclawassistant`
- that name comes from the Slack app identity in Slack itself
- updating local env/config does NOT rename the Slack bot/app

Real Slack-side fix path confirmed in live admin UI:
- open `App Home` for the Slack app
- under `Your App's Presence in Slack`, click `Edit`
- change both fields:
  - `Display Name (Bot Name)`
  - `Default Name`
- save and verify the page shows `App display name saved!`

Observed good target values for Hermes:
- `Display Name (Bot Name): Hermes Agent`
- `Default Name: hermes_agent`

Important behavior note:
- old messages do NOT retroactively change name
- Slack mention autocomplete / visible bot name may lag due to client caching
- after renaming, ask the user to retry mention after refreshing Slack, switching channels, or reopening the compose box

So there are two separate outcomes:

### Local cutover complete
- Hermes uses the correct Slack tokens
- gateway is configured and restarted
- live API auth checks pass

### Slack-side identity cleanup still pending
- bot/app display name in Slack UI can still show an old OpenClaw-era name
- this must be changed manually in Slack App settings
- changing **App Home → App Display Name / Default Name** may update `bots.info` and the app-facing label, but that is NOT the whole story

Important real-world finding:
- Slack can keep a separate legacy bot-user profile with stale fields like:
  - `users.info(user_id=<bot user>) -> real_name = OpenClaw_Assistant`
  - `profile.real_name = OpenClaw_Assistant`
  - `first_name = OpenClaw_Assistant`
- this means the visible sender/app name can already be `Hermes Agent` while some Slack surfaces still render `OpenClaw_Assistant`
- with current bot-token capabilities, `users.profile.set` may fail with `not_allowed_token_type`
- with a normal user OAuth token, changing that bot user profile may still fail without `users.profile:write`

Do not promise that local config changes or App Home renaming will fully remove every old Slack-visible OpenClaw label.
Treat the legacy bot-user profile as a separate cleanup layer.

## Reusable summary for users

When reporting status, be explicit:
- local Hermes cutover is done
- token mapping is corrected
- live auth is verified
- if the bot still shows the old name, that is a Slack App dashboard setting, not a Hermes-side failure

## Real-world blocker pattern: bot can DM out, but users cannot reply

A very important Slack-side failure mode observed in practice:
- Hermes can successfully send a DM to the user
- the user sees the bot message
- but Slack shows: `已關閉傳送訊息到此應用程式`
- users cannot reply in the bot DM / App Home

Interpretation:
- outbound bot auth is working
- workspace selection is likely correct
- the blocker is NOT the Hermes token itself
- the blocker is usually Slack App Home / Messages configuration

Required Slack-side fix:
- open Slack App settings
- go to **App Home**
- enable **Messages Tab**
- enable **Allow users to send Slash commands and messages from the messages tab**

Without this, DM visibility can create a false positive: the user thinks the bot is present, but inbound DM is still disabled.

## Real-world blocker pattern: channel mention still does nothing

If all of these are true:
- bot token auth passes
- app token auth passes
- Hermes can send outbound DM
- user invited / mentioned the bot in a channel
- but the bot still does not react

then check these before blaming Hermes routing logic:

1. Workspace mismatch
- verify the active Slack workspace the user is testing in is the SAME one returned by `auth.test`
- a common mistake is testing in one workspace while Hermes tokens point to another

2. Channel presence
- the bot must actually be in the target channel
- `/invite @BotName` must succeed inside that workspace/channel

3. Event subscriptions
Ensure Slack App bot events include at least:
- `app_mention`
- `message.channels`
- `message.groups`
- `message.im`
- `message.mpim`
- `assistant_thread_started`
- `assistant_thread_context_changed`

4. OAuth scopes
A practical symptom of under-scoping is Slack API returning `missing_scope` for read APIs like:
- `conversations.list`
- `users.info`
- `bots.info`

If you see that, treat channel non-responsiveness as a Slack app config problem first.

## Recommended live cutover sequence

When debugging a real Slack cutover, use this order:

1. Verify bot/app tokens with Slack API
2. Verify which workspace they point to
3. Send an outbound DM successfully
4. Check whether the user can reply in DM
5. If DM reply is disabled, fix App Home Messages Tab first
6. Only then test channel mention flow
7. If channel mention still fails, inspect bot membership + scopes + event subscriptions

This sequence avoids wasting time on channel debugging before the app can even receive replies in App Home.

## 6.10 Slack MCP is a second control path, not a fix for bot inbound events

A reusable debugging lesson from this cutover:

- yes, Slack can be integrated through MCP servers
- no, Slack MCP does NOT automatically fix `@bot` mention flows in channels

What Slack MCP is good for:
- proactively reading channels / threads / users
- proactively posting messages or replies
- giving Hermes a tool-driven backdoor into Slack when normal bot UX is unreliable

What Slack MCP does NOT guarantee:
- Slack users mentioning the bot in-channel will trigger Hermes automatically
- App Home / Socket Mode / Event Subscription issues disappear
- broken `app_mention` / `message.channels` delivery gets repaired

Practical guidance:
- use Slack MCP as a parallel fallback path when the user needs Slack operational access now
- keep debugging the real Slack bot inbound path separately
- explain the distinction clearly to the user so MCP is not mistaken for a complete replacement of bot events

In short:
- Slack bot integration = event-driven inbound UX
- Slack MCP integration = tool-driven outbound/control UX

Both are valuable, but they solve different problems.

## Pitfalls

- trusting pasted token labels instead of token prefixes
- assigning `xapp-...` to `SLACK_BOT_TOKEN`
- assigning `xoxb-...` to `SLACK_APP_TOKEN`
- treating app-token lock conflicts as invalid credentials
- assuming lack of log lines means Slack auth failed
- promising to remove Slack-visible OpenClaw naming without changing the Slack App settings in Slack itself

## Done when

A Slack cutover is complete when:
- Hermes env contains correctly mapped Slack tokens
- live Slack auth checks pass
- Hermes gateway has been restarted
- Slack shows as configured in Hermes status
- any remaining old bot/app display name is clearly identified as Slack-side branding work, not local config debt
