---
name: hermes-discord-test-mock-hardening
description: Stabilize Hermes Discord adapter tests when discord.py is missing or partially mocked, especially in full CI runs where import-safety tests leave gateway.platforms.discord.discord as None.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, discord, pytest, ci, mocks, regression]
    related_skills: [systematic-debugging, github-pr-workflow]
---

# Hermes Discord Test Mock Hardening

Use when Hermes Discord tests pass individually but fail in full CI, especially with errors like:
- `AttributeError: 'NoneType' object has no attribute 'DMChannel'`
- `/skill` registration failing because `app_commands.Group` or `app_commands.Command` is missing
- reply-mode tests not dispatching because mention / auto-thread logic short-circuits in CI

## Root cause pattern

Hermes has two different test modes around `gateway.platforms.discord`:
1. import-safety tests intentionally import the module with `discord` unavailable and assert `module.discord is None`
2. many Discord tests then monkeypatch attributes onto `discord_platform.discord`

In a full test run, those later tests can inherit the `discord is None` state and crash unless they rebuild a lightweight namespace first.

A second issue is that isolated test files may pass while full-suite CI fails because `_handle_message()` is gated by environment-driven mention / auto-thread behavior. If the fixture doesn't disable those gates, `handle_message` may never be awaited.

## Fix strategy

### 1. Preserve import-safety contract in production code

Do **not** change the adapter import fallback from:

```python
except ImportError:
    DISCORD_AVAILABLE = False
    discord = None
```

Some tests explicitly require `module.discord is None` when discord.py is missing.

### 2. Make slash-command registration tolerant of thin mocks

In `gateway/platforms/discord.py`, inside `_register_skill_group()`:
- read `app_commands = getattr(discord, "app_commands", None)`
- use `getattr(..., "describe", fallback)`
- fall back to local lightweight `Group` and `Command` classes if the mock lacks them

This keeps real discord.py behavior unchanged while allowing minimal unit-test mocks to work.

### 3. In test fixtures, recreate `discord_platform.discord` when it is None

Before monkeypatching `DMChannel`, `Thread`, or `ForumChannel`, add:

```python
if discord_platform.discord is None:
    monkeypatch.setattr(discord_platform, "discord", SimpleNamespace(), raising=False)
```

Then patch the required classes onto that namespace.

Apply this pattern in Discord test fixtures that directly touch `discord_platform.discord`.

### 4. For reply-mode / `_handle_message()` tests, disable unrelated gating

In fixtures that expect `handle_message` to be awaited, force these env vars:

```python
monkeypatch.setenv("DISCORD_REQUIRE_MENTION", "false")
monkeypatch.setenv("DISCORD_AUTO_THREAD", "false")
```

Otherwise CI may skip dispatch entirely because:
- the message is treated as needing a mention, or
- auto-thread logic changes routing/flow

## Verification sequence

Run this progression:

```bash
python -m pytest tests/gateway/test_discord_reply_mode.py -q
python -m pytest tests/gateway/test_discord_*.py tests/agent/test_auxiliary_named_custom_providers.py tests/hermes_cli/test_api_key_providers.py -q
```

If the subset passes, push and verify the real fork CI run rather than assuming success from local partial tests.

## Pitfalls

- Do not replace `discord = None` with a namespace in the production import fallback; that breaks import-safety tests.
- A fix that only makes `test_discord_reply_mode.py` pass locally may still fail in full CI if another test imported the module under the missing-discord path first.
- If reply-mode assertions fail with `handle_message.await_args is None`, suspect mention/auto-thread env gating before changing adapter logic.

## Related concurrent fixes from the same PR class

When this failure cluster appears together with provider tests:
- Copilot runtime may need a base URL fallback from provider registry if pool/API-key credentials omit `base_url`
- Vision auto-routing should preserve an explicitly configured main model before falling back to provider-specific vision defaults

These are separate root causes, but they often appear in the same fork-CI cleanup pass.