#!/usr/bin/env python3
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

import fcntl

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hermes_constants import get_hermes_home
from hermes_cli.env_loader import load_hermes_dotenv

TEAM_ID = "T0AC8E2D5DH"
MCP_STDIO = "npx -y @zencoderai/slack-mcp-server --transport stdio"
STATE_PATH = get_hermes_home() / "slack_mcp_boss_mode.json"
WATCHER_STATE_PATH = get_hermes_home() / "slack_mcp_watcher_state.json"
BOT_USER_ID = "U0AD94D3J3S"
BOT_ID = "B0AC8DM14CB"


def load_env() -> tuple[str, str]:
    load_hermes_dotenv(hermes_home=get_hermes_home())
    bot = os.getenv("SLACK_BOT_TOKEN", "").strip()
    user = os.getenv("SLACK_USER_OAUTH_TOKEN", "").strip()
    if not bot:
        raise SystemExit("Missing SLACK_BOT_TOKEN")
    if not user:
        raise SystemExit("Missing SLACK_USER_OAUTH_TOKEN")
    return bot, user


@contextmanager
def _locked_json_handle(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")
    with open(path, "r+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield handle
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_json_from_handle(handle) -> dict:
    handle.seek(0)
    raw = handle.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _write_json_to_handle(handle, data: dict) -> None:
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps(data, ensure_ascii=False, indent=2))
    handle.flush()
    os.fsync(handle.fileno())


def load_state() -> dict:
    with _locked_json_handle(STATE_PATH) as handle:
        return _load_json_from_handle(handle)


def save_state(state: dict) -> None:
    with _locked_json_handle(STATE_PATH) as handle:
        _write_json_to_handle(handle, state)


def load_watcher_state() -> dict:
    with _locked_json_handle(WATCHER_STATE_PATH) as handle:
        return _load_json_from_handle(handle)


def save_watcher_state(state: dict) -> None:
    with _locked_json_handle(WATCHER_STATE_PATH) as handle:
        _write_json_to_handle(handle, state)


def _pid_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def _watch_loop_pids() -> list[int]:
    proc = subprocess.run(
        ["ps", "-ax", "-o", "pid=,command="],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        return []
    pids = []
    marker = "python scripts/slack_mcp_boss_mode.py watch-loop"
    for line in (proc.stdout or "").splitlines():
        raw = line.strip()
        if not raw or marker not in raw:
            continue
        parts = raw.split(None, 1)
        if len(parts) != 2:
            continue
        pid_text, command = parts
        command = command.strip()
        if not command.startswith(marker):
            continue
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if _pid_running(pid):
            pids.append(pid)
    return sorted(set(pids))


def cleanup_stale_watchers() -> dict:
    tracked = load_watcher_state().get("pid")
    pids = _watch_loop_pids()
    stale = [pid for pid in pids if pid != tracked]
    killed = []
    for pid in stale:
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except ProcessLookupError:
            continue
    return {
        "tracked_pid": tracked,
        "all_pids": pids,
        "stale_pids": stale,
        "killed_pids": killed,
    }


def ensure_singleton_watcher(channel_name: str) -> None:
    state = load_watcher_state()
    existing_pid = state.get("pid")
    if existing_pid and existing_pid != os.getpid() and _pid_running(existing_pid):
        raise SystemExit(f"watch-loop 已在執行中 (pid={existing_pid}, channel=#{state.get('channel_name', channel_name)})")
    save_watcher_state(
        {
            "pid": os.getpid(),
            "channel_name": channel_name,
            "started_at": time.time(),
            "log_path": str((ROOT / 'tmp' / 'slack_watch_loop.log').resolve()),
        }
    )


def clear_singleton_watcher() -> None:
    state = load_watcher_state()
    if state.get("pid") == os.getpid():
        save_watcher_state({})


def watcher_status() -> dict:
    state = load_watcher_state()
    pid = state.get("pid")
    all_pids = _watch_loop_pids()
    return {
        "pid": pid,
        "running": _pid_running(pid),
        "channel_name": state.get("channel_name"),
        "started_at": state.get("started_at"),
        "log_path": state.get("log_path"),
        "all_watch_loop_pids": all_pids,
        "duplicate_watchers": len(all_pids),
    }


def ensure_watcher_running(channel_name: str) -> dict:
    state = load_watcher_state()
    pid = state.get("pid")
    if pid and _pid_running(pid):
        return {
            "ok": True,
            "action": "already_running",
            "pid": pid,
            "channel_name": state.get("channel_name", channel_name),
            "log_path": state.get("log_path"),
        }
    return {
        "ok": True,
        "action": "needs_start",
        "channel_name": channel_name,
        "log_path": str((ROOT / 'tmp' / 'slack_watch_loop.log').resolve()),
    }


def _lane_registry(state: dict) -> dict:
    return state.setdefault("lane_registry", {})


def _queue_state(state: dict) -> dict:
    return state.setdefault("execution_queue", {"pending": [], "active": None, "history": []})


def register_lane(channel: dict, source_message: dict, kickoff_reply: dict | None = None) -> dict:
    state = load_state()
    registry = _lane_registry(state)
    source_ts = str(source_message.get("ts", ""))
    lane_id = f"{channel['id']}:{source_ts}"
    entry = registry.get(lane_id, {})
    now = time.time()
    kickoff_reply = kickoff_reply or {"ts": "", "message": {"thread_ts": source_ts}}
    entry.update(
        {
            "lane_id": lane_id,
            "channel_id": channel["id"],
            "channel_name": channel["name"],
            "source_ts": source_ts,
            "source_text": clean_text(source_message.get("text", "")),
            "thread_ts": str(kickoff_reply.get("message", {}).get("thread_ts") or source_ts),
            "kickoff_ts": str(kickoff_reply.get("ts", "")),
            "status": entry.get("status") or "kickoff_sent",
            "created_at": entry.get("created_at") or now,
            "last_updated_at": now,
        }
    )
    registry[lane_id] = entry
    save_state(state)
    return entry


def list_lanes(channel_id: str | None = None) -> list[dict]:
    state = load_state()
    registry = _lane_registry(state)
    rows = list(registry.values())
    if channel_id:
        rows = [row for row in rows if row.get("channel_id") == channel_id]
    rows.sort(key=lambda row: row.get("created_at", 0), reverse=True)
    return rows


def get_lane(lane_id: str) -> dict | None:
    state = load_state()
    return _lane_registry(state).get(lane_id)


def update_lane(lane_id: str, **fields) -> dict:
    state = load_state()
    registry = _lane_registry(state)
    lane = dict(registry.get(lane_id, {}))
    if not lane:
        raise SystemExit(f"Lane not found: {lane_id}")
    lane.update(fields)
    lane["last_updated_at"] = time.time()
    registry[lane_id] = lane
    save_state(state)
    return lane


TERMINAL_LANE_STATUSES = {"agent_replied", "agent_error", "ignored_test_lane", "completed", "closed", "blocked", "stale"}


def reconcile_stale_lanes(max_age_seconds: int = 1800) -> dict:
    now = time.time()
    state = load_state()
    registry = _lane_registry(state)
    stale_lanes = []
    for lane_id, lane in list(registry.items()):
        status = lane.get("status")
        if status in TERMINAL_LANE_STATUSES:
            continue
        last_updated = float(lane.get("last_updated_at") or lane.get("created_at") or 0)
        if last_updated and now - last_updated > max_age_seconds:
            lane = dict(lane)
            lane["status"] = "stale"
            lane["stale_reason"] = f"inactive_for_{max_age_seconds}s"
            lane["stale_marked_at"] = now
            lane["last_updated_at"] = now
            registry[lane_id] = lane
            stale_lanes.append(lane_id)
    if stale_lanes:
        save_state(state)
    return {"ok": True, "stale_lanes": stale_lanes, "count": len(stale_lanes), "max_age_seconds": max_age_seconds}


def enqueue_lane(lane_id: str) -> dict:
    state = load_state()
    queue = _queue_state(state)
    pending = queue.setdefault("pending", [])
    if lane_id not in pending and queue.get("active") != lane_id:
        pending.append(lane_id)
    queue["pending"] = pending
    save_state(state)
    return queue


def queue_status() -> dict:
    state = load_state()
    queue = _queue_state(state)
    registry = _lane_registry(state)
    stale_lane_count = sum(1 for lane in registry.values() if lane.get("status") == "stale")
    return {
        "active": queue.get("active"),
        "pending": queue.get("pending", []),
        "history": queue.get("history", [])[-10:],
        "last_result": queue.get("last_result"),
        "stale_lane_count": stale_lane_count,
    }


def run_queue_once() -> dict:
    state = load_state()
    queue = _queue_state(state)
    pending = queue.get("pending", [])
    if queue.get("active"):
        return {"ok": False, "reason": "worker_busy", "active": queue.get("active")}
    if not pending:
        return {"ok": True, "action": "noop", "message": "queue 目前沒有待執行 lane"}
    lane_id = pending.pop(0)
    queue["active"] = lane_id
    queue["pending"] = pending
    save_state(state)
    try:
        result = execute_lane(lane_id)
        state = load_state()
        queue = _queue_state(state)
        history = queue.setdefault("history", [])
        history.append({
            "lane_id": lane_id,
            "finished_at": time.time(),
            "status": result.get("lane", {}).get("status"),
            "ok": True,
        })
        queue["history"] = history[-50:]
        queue["last_result"] = {
            "lane_id": lane_id,
            "ok": True,
            "status": result.get("lane", {}).get("status"),
            "finished_at": time.time(),
        }
        save_state(state)
        return {"ok": True, "action": "executed", "lane_id": lane_id, "result": result}
    except BaseException as exc:
        state = load_state()
        queue = _queue_state(state)
        history = queue.setdefault("history", [])
        history.append({
            "lane_id": lane_id,
            "finished_at": time.time(),
            "status": "error",
            "ok": False,
            "error": str(exc),
        })
        queue["history"] = history[-50:]
        queue["last_result"] = {
            "lane_id": lane_id,
            "ok": False,
            "status": "error",
            "error": str(exc),
            "finished_at": time.time(),
        }
        save_state(state)
        return {"ok": False, "action": "error", "lane_id": lane_id, "error": str(exc)}
    finally:
        state = load_state()
        queue = _queue_state(state)
        if queue.get("active") == lane_id:
            queue["active"] = None
            save_state(state)


def slack_api(token: str, method: str, params: dict | None = None, post: bool = False) -> dict:
    params = params or {}
    if post:
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            f"https://slack.com/api/{method}",
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
    else:
        url = f"https://slack.com/api/{method}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    if not data.get("ok"):
        raise RuntimeError(f"Slack API {method} failed: {data.get('error')}")
    return data


def list_channels(user_token: str) -> list[dict]:
    data = slack_api(
        user_token,
        "conversations.list",
        {"types": "public_channel", "exclude_archived": "true", "limit": "200"},
    )
    rows = []
    for c in data.get("channels", []):
        rows.append(
            {
                "id": c["id"],
                "name": c["name"],
                "is_member": c.get("is_member", False),
                "num_members": c.get("num_members", 0),
                "purpose": c.get("purpose", {}).get("value", ""),
            }
        )
    return rows


def resolve_channel(user_token: str, ident: str) -> dict:
    channels = list_channels(user_token)
    if ident.startswith("C"):
        for c in channels:
            if c["id"] == ident:
                return c
    plain = ident.removeprefix("#")
    for c in channels:
        if c["name"] == plain:
            return c
    raise SystemExit(f"Channel not found: {ident}")


def get_default_channel(user_token: str) -> dict:
    state = load_state()
    ident = state.get("default_channel") or state.get("default_channel_id")
    if not ident:
        raise SystemExit("尚未設定預設控盤頻道，先執行 set-default <channel>")
    return resolve_channel(user_token, ident)


def channel_history(user_token: str, channel_id: str, limit: int = 12) -> list[dict]:
    data = slack_api(user_token, "conversations.history", {"channel": channel_id, "limit": str(limit)})
    return data.get("messages", [])


def user_name_map(user_token: str) -> dict[str, str]:
    data = slack_api(user_token, "users.list", {"limit": "200"})
    out = {}
    for m in data.get("members", []):
        profile = m.get("profile", {})
        out[m.get("id", "")] = profile.get("display_name") or profile.get("real_name") or m.get("name") or m.get("id")
    return out


def clean_text(text: str) -> str:
    return " ".join((text or "").replace("\n", " ").split())


def _visible_messages(messages: list[dict]) -> list[dict]:
    visible = []
    for m in messages:
        subtype = m.get("subtype")
        if subtype in {"channel_join", "channel_leave", "channel_purpose", "channel_topic"}:
            continue
        txt = clean_text(m.get("text", ""))
        if not txt:
            continue
        visible.append(m | {"_clean": txt})
    return visible


def summarize_messages(channel: dict, messages: list[dict], names: dict[str, str]) -> str:
    recent = _visible_messages(messages)[:6]
    speakers = Counter(names.get(m.get("user", ""), m.get("user", "系統")) for m in recent)
    top_speakers = "、".join(name for name, _ in speakers.most_common(3)) or "目前看不到有效對話"
    key_lines = []
    for m in recent[:3]:
        who = names.get(m.get("user", ""), m.get("user", "系統"))
        key_lines.append(f"- {who}：{m['_clean'][:120]}")
    latest = recent[0]["_clean"][:140] if recent else "目前沒有可讀的新訊息"
    return (
        f"頻道：#{channel['name']}\n"
        f"結論：最近可讀訊息共 {len(recent)} 則，最新重點是「{latest}」。\n"
        f"現況：主要發言者是 {top_speakers}。\n"
        f"你現在要決定什麼：若這是要我跟進的頻道，就指定這個頻道做持續控盤。\n"
        f"關鍵片段：\n" + ("\n".join(key_lines) if key_lines else "- 目前沒有可用片段")
    )


def build_control_status(channel: dict, messages: list[dict], names: dict[str, str]) -> str:
    recent = _visible_messages(messages)[:8]
    if not recent:
        return (
            f"控盤頻道：#{channel['name']}\n"
            "結論：目前沒有可讀的新訊息。\n"
            "現況：這個頻道可作為固定控盤頻道，但現在沒有新的對話動作。\n"
            "下一步：你可以直接叫我在這個頻道發一則決策訊息。"
        )

    speaker_counts = Counter(names.get(m.get("user", ""), m.get("user", "系統")) for m in recent)
    top_speakers = "、".join(name for name, _ in speaker_counts.most_common(3))
    latest = recent[0]
    latest_text = latest["_clean"][:140]
    mention_like = [
        m for m in recent
        if "<@B0AC8DM14CB>" in m["_clean"] or "@Hermes Agent" in m["_clean"] or "頻道測試" in m["_clean"]
    ]
    highlights = []
    for m in recent[:3]:
        who = names.get(m.get("user", ""), m.get("user", "系統"))
        highlights.append(f"- {who}：{m['_clean'][:120]}")
    action_line = "若你要，我可以直接把這個頻道當固定控盤主線。"
    if mention_like:
        action_line = f"最近有 {len(mention_like)} 則點名或測試訊息，適合直接升級成固定控盤主線。"
    return (
        f"控盤頻道：#{channel['name']}\n"
        f"結論：最新重點是「{latest_text}」。\n"
        f"現況：最近主要發言者是 {top_speakers}。\n"
        f"下一步：{action_line}\n"
        f"關鍵片段：\n" + "\n".join(highlights)
    )


def mcporter_call(tool: str, **kwargs) -> dict:
    env = os.environ.copy()
    env["SLACK_TEAM_ID"] = TEAM_ID
    cmd = ["mcporter", "call", "--stdio", MCP_STDIO, tool]
    for k, v in kwargs.items():
        cmd.append(f"{k}={v}")
    cmd.extend(["--output", "json"])
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"mcporter failed: {proc.returncode}")
    return json.loads(proc.stdout)


def post_message(channel_id: str, text: str) -> dict:
    return mcporter_call("slack_post_message", channel_id=channel_id, text=text)


def reply_thread(channel_id: str, thread_ts: str, text: str) -> dict:
    env = os.environ.copy()
    env["SLACK_TEAM_ID"] = TEAM_ID
    payload = json.dumps({"channel_id": channel_id, "thread_ts": str(thread_ts), "text": text}, ensure_ascii=False)
    cmd = [
        "mcporter", "call",
        "--stdio", MCP_STDIO,
        "slack_reply_to_thread",
        "--args", payload,
        "--output", "json",
    ]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"mcporter failed: {proc.returncode}")
    return json.loads(proc.stdout)


def classify_lane_text(text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"kind": "normal", "skip_agent": False, "reason": None}
    lowered = cleaned.lower()
    skip_markers = [
        "請忽略",
        "ignore",
        "自測",
        "自我測試",
        "測試",
        "驗證",
        "watcher 重啟後自動驗證",
        "queue 可觀測性驗證",
        "端到端自測",
    ]
    matched = [marker for marker in skip_markers if marker in cleaned or marker in lowered]
    if matched:
        return {
            "kind": "test_or_ignore",
            "skip_agent": True,
            "reason": f"matched:{','.join(matched[:4])}",
        }
    return {"kind": "normal", "skip_agent": False, "reason": None}


def build_thread_kickoff(channel_name: str, text: str) -> str:
    cleaned = clean_text(text)
    lane_class = classify_lane_text(cleaned)
    if lane_class["skip_agent"]:
        return (
            "我先把這則當測試訊息收著，先不進正式執行。\n"
            "如果你後面改成正式交辦，我就直接在這條 thread 接下去。"
        )
    return (
        "收到，這條 thread 我直接接手。\n"
        "後續我就留在這裡往下推，不在主頻道刷細節。"
    )


def build_lane_started(text: str) -> str:
    return (
        "我先接住這個方向。\n"
        "現在會先把目標釐清、拆第一批動作，順手看看有沒有明顯卡點。"
    )


def build_execution_agent_prompt(lane: dict, followup_text: str | None = None) -> str:
    if followup_text:
        return (
            "你正在延續同一條 Slack work-lane。"
            "請把使用者剛剛在 thread 裡補充的想法，當成同一段持續對話直接接下去處理。"
            "回覆要像終端機裡同一段工作對話：自然、直接、有進度感，不要重新自我介紹，不要重講整段 kickoff。"
            "不要每次都硬切『結論 / 現況 / 下一步』三個標題；只有真的有助於理解時才保留。"
            "優先用 2-4 個短段落或短句，像真人在 thread 裡接話。"
            "第一句要明確接住對方剛補充的內容，例如：『你剛補的這點我收到了』、『這個方向我改一下』、『我先把這段納進來』。"
            "若使用者是在修正方向，就明確說你已調整；若他是在補資料，就明確說你已納入；若他在追問進度，就直接講你做到哪。"
            "避免工程術語、避免過度條列、避免像報表。\n\n"
            f"lane_id: {lane.get('lane_id')}\n"
            f"原始交辦: {lane.get('source_text','')}\n"
            f"使用者剛補充: {followup_text}"
        )
    return (
        "你是 Slack work-lane 的執行子代理。"
        "請直接根據交辦內容，產出一則適合回在 thread 裡的第一版執行回覆。"
        "風格要像終端機裡一起工作的對話：自然、直接、好讀，不要像制式報表。"
        "可保留很輕的結構感，但不要每次都硬切三段模板；優先用 2-4 個短段落或短句。"
        "第一句先講你已經接住這件事，再講你現在怎麼理解，最後帶到你接著怎麼做。"
        "不要解釋你是 AI，不要要求使用者重複需求，不要輸出英文介面語。\n\n"
        f"lane_id: {lane.get('lane_id')}\n"
        f"channel: #{lane.get('channel_name')}\n"
        f"source_text: {lane.get('source_text','')}"
    )


def extract_session_id(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"(?mi)^session_id:\s*(\S+)\s*$", text)
    return match.group(1).strip() if match else None


def strip_session_metadata(text: str) -> str:
    if not text:
        return text
    cleaned = re.sub(r"(?mi)^session_id:\s*\S+\s*$", "", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def run_lane_agent(lane: dict, followup_text: str | None = None) -> dict:
    prompt = build_execution_agent_prompt(lane, followup_text=followup_text)
    cmd = [
        "hermes", "chat",
        "-Q",
        "-q", followup_text or prompt,
        "-t", "terminal,file",
        "--source", "tool",
        "--yolo",
    ]
    session_id = lane.get("session_id")
    if followup_text and session_id:
        cmd.extend(["--resume", str(session_id)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"hermes chat failed: {proc.returncode}")
    output = (proc.stdout or "").strip()
    return {
        "prompt": prompt,
        "output": strip_session_metadata(output),
        "session_id": extract_session_id(output) or (str(session_id) if session_id else None),
        "raw_output": output,
    }


def execute_lane(lane_id: str, followup_text: str | None = None, followup_ts: str | None = None) -> dict:
    lane = get_lane(lane_id)
    if not lane:
        raise SystemExit(f"Lane not found: {lane_id}")
    lane_updates = {"status": "agent_running"}
    if followup_ts:
        lane_updates["last_user_reply_ts"] = str(followup_ts)
    update_lane(lane_id, **lane_updates)
    agent_result = run_lane_agent(lane, followup_text=followup_text)
    thread_ts = str(lane.get("thread_ts") or lane.get("source_ts") or "")
    reply = reply_thread(lane["channel_id"], thread_ts, agent_result["output"])
    updated = update_lane(
        lane_id,
        status="agent_replied",
        agent_reply_ts=str(reply.get("ts", "")),
        agent_reply_preview=agent_result["output"][:400],
        session_id=agent_result.get("session_id"),
        last_seen_thread_reply_ts=str(followup_ts) if followup_ts else lane.get("last_seen_thread_reply_ts"),
    )
    return {"lane": updated, "reply": reply, "agent": agent_result}


def build_lane_governance_reply(status: str, note: str | None = None) -> str:
    note = clean_text(note or "")
    if status == "blocked":
        base = "結論：這條 lane 已標記為 blocked。\n現況：目前先停止自動往下推進，等待阻塞條件解除。\n下一步：請先處理阻塞點，之後可再恢復或改派。"
    elif status == "completed":
        base = "結論：這條 lane 已完成主要執行。\n現況：thread 內的工作已告一段落，可供主頻道做 closeout 判斷。\n下一步：若沒有新變更，建議直接進 closeout。"
    elif status == "closed":
        base = "結論：這條 lane 已正式關閉。\n現況：thread 內工作已結案，不再持續自動推進。\n下一步：若有新需求，請開新 lane 或重新交辦。"
    else:
        raise SystemExit(f"Unsupported lane governance status: {status}")
    if note:
        base += f"\n補充：{note[:240]}"
    return base


def transition_lane(lane_id: str, status: str, note: str | None = None) -> dict:
    lane = get_lane(lane_id)
    if not lane:
        raise SystemExit(f"Lane not found: {lane_id}")
    if status not in {"blocked", "completed", "closed"}:
        raise SystemExit(f"Unsupported transition status: {status}")
    thread_ts = str(lane.get("thread_ts") or lane.get("source_ts") or "")
    reply = reply_thread(lane["channel_id"], thread_ts, build_lane_governance_reply(status, note))
    updated = update_lane(
        lane_id,
        status=status,
        governance_note=clean_text(note or "") or None,
        governance_reply_ts=str(reply.get("ts", "")),
    )
    return {"lane": updated, "reply": reply}


def advance_lane(channel: dict, source_message: dict, lane_entry: dict) -> dict:
    thread_ts = str(lane_entry.get("thread_ts") or source_message.get("ts") or "")
    lane_class = classify_lane_text(source_message.get("text", ""))
    if lane_class["skip_agent"]:
        summary = reply_thread(
            channel["id"],
            thread_ts,
            "這條我先當測試訊息收著，暫時不往正式執行推。\n如果你後面改成正式交辦，我就直接在這條 thread 接下去。",
        )
        state = load_state()
        registry = _lane_registry(state)
        lane_id = lane_entry["lane_id"]
        current = registry.get(lane_id, lane_entry)
        current.update(
            {
                "status": "ignored_test_lane",
                "classification": lane_class["kind"],
                "classification_reason": lane_class["reason"],
                "ignored_ts": str(summary.get("ts", "")),
                "last_updated_at": time.time(),
            }
        )
        registry[lane_id] = current
        save_state(state)
        return {"lane": current, "reply": summary, "execution_reply": None, "parent_summary": None}
    state = load_state()
    registry = _lane_registry(state)
    lane_id = lane_entry["lane_id"]
    current = registry.get(lane_id, lane_entry)
    current.update(
        {
            "status": "executing",
            "classification": lane_class["kind"],
            "classification_reason": lane_class["reason"],
            "plan_ts": str(current.get("plan_ts") or ""),
            "execution_ts": str(current.get("execution_ts") or ""),
            "last_updated_at": time.time(),
        }
    )
    registry[lane_id] = current
    save_state(state)
    return {"lane": current, "reply": None, "execution_reply": None, "parent_summary": None}


def _thread_lane_state(state: dict, channel_id: str) -> dict:
    lanes = state.setdefault("thread_lane", {})
    lane_state = lanes.setdefault(channel_id, {"processed_top_level_ts": [], "in_flight_top_level_ts": [], "last_seen_ts": "0", "active_from_ts": None})
    lane_state.setdefault("processed_top_level_ts", [])
    lane_state.setdefault("in_flight_top_level_ts", [])
    lane_state.setdefault("last_seen_ts", "0")
    lane_state.setdefault("active_from_ts", None)
    return lane_state


def detect_new_top_level_task(user_token: str, channel: dict, limit: int = 12) -> dict | None:
    state = load_state()
    lane_state = _thread_lane_state(state, channel["id"])
    processed = set(lane_state.get("processed_top_level_ts", []))
    messages = channel_history(user_token, channel["id"], limit=limit)
    active_from_ts = lane_state.get("active_from_ts")
    if not active_from_ts:
        latest_ts = max((str(m.get("ts", "0")) for m in messages), default="0")
        lane_state["active_from_ts"] = latest_ts
        lane_state["last_seen_ts"] = latest_ts
        save_state(state)
        return None
    candidate = None
    latest_seen = lane_state.get("last_seen_ts", active_from_ts)
    for message in messages:
        ts = str(message.get("ts", "0"))
        if ts > latest_seen:
            latest_seen = ts
        if ts <= str(active_from_ts):
            continue
        msg_user = message.get("user")
        msg_bot_id = message.get("bot_id")
        if msg_user == BOT_USER_ID or msg_bot_id == BOT_ID:
            continue
        if message.get("thread_ts"):
            continue
        subtype = message.get("subtype")
        if subtype:
            continue
        text = clean_text(message.get("text", ""))
        if not text:
            continue
        if ts in processed:
            continue
        candidate = message
        break
    lane_state["last_seen_ts"] = latest_seen
    save_state(state)
    return candidate


def thread_history(user_token: str, channel_id: str, thread_ts: str, limit: int = 20) -> list[dict]:
    data = slack_api(user_token, "conversations.replies", {"channel": channel_id, "ts": str(thread_ts), "limit": str(limit)})
    return data.get("messages", [])


def detect_new_lane_reply(user_token: str, channel: dict, limit: int = 20) -> dict | None:
    terminal_statuses = {"closed", "completed", "blocked", "ignored_test_lane"}
    for lane in list_lanes(channel["id"]):
        if lane.get("status") in terminal_statuses:
            continue
        thread_ts = str(lane.get("thread_ts") or lane.get("source_ts") or "")
        if not thread_ts:
            continue
        messages = thread_history(user_token, channel["id"], thread_ts, limit=limit)
        last_seen = str(
            lane.get("last_seen_thread_reply_ts")
            or lane.get("agent_reply_ts")
            or lane.get("execution_ts")
            or lane.get("plan_ts")
            or lane.get("kickoff_ts")
            or lane.get("source_ts")
            or "0"
        )
        latest_seen = last_seen
        candidate = None
        for message in sorted(messages, key=lambda item: str(item.get("ts", "0"))):
            ts = str(message.get("ts", "0"))
            if ts > latest_seen:
                latest_seen = ts
            if ts <= last_seen or ts == str(lane.get("source_ts") or ""):
                continue
            msg_user = message.get("user")
            msg_bot_id = message.get("bot_id")
            if msg_user == BOT_USER_ID or msg_bot_id == BOT_ID:
                continue
            if message.get("subtype"):
                continue
            text = clean_text(message.get("text", ""))
            if not text:
                continue
            candidate = message
            break
        if candidate:
            return {
                "lane": lane,
                "message": candidate,
                "latest_seen": latest_seen,
            }
        if latest_seen != last_seen:
            update_lane(lane["lane_id"], last_seen_thread_reply_ts=latest_seen)
    return None


def claim_top_level_task(channel_id: str, ts: str) -> bool:
    with _locked_json_handle(STATE_PATH) as handle:
        state = _load_json_from_handle(handle)
        lane_state = _thread_lane_state(state, channel_id)
        processed = set(lane_state.get("processed_top_level_ts", []))
        in_flight = lane_state.setdefault("in_flight_top_level_ts", [])
        if ts in processed or ts in in_flight:
            return False
        in_flight.append(ts)
        lane_state["in_flight_top_level_ts"] = in_flight[-50:]
        _write_json_to_handle(handle, state)
        return True


def release_top_level_task(channel_id: str, ts: str, processed: bool) -> None:
    with _locked_json_handle(STATE_PATH) as handle:
        state = _load_json_from_handle(handle)
        lane_state = _thread_lane_state(state, channel_id)
        in_flight = [item for item in lane_state.get("in_flight_top_level_ts", []) if item != ts]
        lane_state["in_flight_top_level_ts"] = in_flight[-50:]
        if processed:
            seen = lane_state.setdefault("processed_top_level_ts", [])
            if ts not in seen:
                seen.append(ts)
            lane_state["processed_top_level_ts"] = seen[-200:]
        _write_json_to_handle(handle, state)


def mark_processed(channel_id: str, ts: str) -> None:
    release_top_level_task(channel_id, ts, processed=True)


def watch_once(user_token: str, channel: dict) -> dict:
    reply_candidate = detect_new_lane_reply(user_token, channel)
    if reply_candidate:
        lane = reply_candidate["lane"]
        message = reply_candidate["message"]
        ts = str(message.get("ts", ""))
        text = clean_text(message.get("text", ""))
        queue_result = {
            "ok": True,
            "action": "thread_reply_processed",
            "lane_id": lane["lane_id"],
        }
        result = execute_lane(lane["lane_id"], followup_text=text, followup_ts=ts)
        tracked_lane = update_lane(
            lane["lane_id"],
            queue_action=queue_result["action"],
            queue_ok=True,
            queue_finished_at=time.time(),
        )
        return {
            "ok": True,
            "action": "thread_reply",
            "channel": channel["name"],
            "lane": tracked_lane,
            "source_ts": lane.get("source_ts"),
            "followup_ts": ts,
            "followup_text": text,
            "agent_reply": result.get("reply"),
            "queue_result": queue_result,
        }

    candidate = detect_new_top_level_task(user_token, channel)
    if not candidate:
        return {
            "ok": True,
            "action": "noop",
            "channel": channel["name"],
            "message": "目前沒有新的 top-level 使用者交辦需要開 thread lane",
        }
    thread_ts = str(candidate["ts"])
    if not claim_top_level_task(channel["id"], thread_ts):
        return {
            "ok": True,
            "action": "noop_claimed",
            "channel": channel["name"],
            "source_ts": thread_ts,
            "message": "這則 top-level 交辦已被其他值班流程接手",
        }
    processed_successfully = False
    try:
        lane_entry = register_lane(channel, candidate, kickoff_reply=None)
        advance = advance_lane(channel, candidate, lane_entry)
        state = load_state()
        _lane_registry(state)[advance["lane"]["lane_id"]] = advance["lane"]
        save_state(state)
        lane_id = advance["lane"]["lane_id"]
        if advance["lane"].get("status") == "ignored_test_lane":
            tracked_lane = update_lane(
                lane_id,
                queue_action="skipped_test_lane",
                queue_ok=True,
                queue_finished_at=time.time(),
            )
            processed_successfully = True
            return {
                "ok": True,
                "action": "thread_kickoff",
                "channel": channel["name"],
                "source_ts": thread_ts,
                "source_text": candidate.get("text", ""),
                "reply_ts": None,
                "lane": tracked_lane,
                "plan_reply": advance["reply"],
                "execution_reply": None,
                "parent_summary": None,
                "agent_reply": None,
                "queue_result": {"ok": True, "action": "skipped_test_lane", "lane_id": lane_id},
                "reply": None,
            }
        enqueue_lane(lane_id)
        queue_result = run_queue_once()
        executed_lane = queue_result.get("result", {}).get("lane") if queue_result.get("ok") else None
        executed_reply = queue_result.get("result", {}).get("reply") if queue_result.get("ok") else None
        lane_updates = {
            "queue_action": queue_result.get("action"),
            "queue_ok": queue_result.get("ok"),
        }
        if queue_result.get("ok"):
            lane_updates["queue_finished_at"] = time.time()
        else:
            lane_updates["queue_error"] = queue_result.get("error") or queue_result.get("reason")
            lane_updates["status"] = "agent_error"
        tracked_lane = update_lane(lane_id, **lane_updates)
        processed_successfully = True
        return {
            "ok": True,
            "action": "thread_kickoff",
            "channel": channel["name"],
            "source_ts": thread_ts,
            "source_text": candidate.get("text", ""),
            "reply_ts": None,
            "lane": executed_lane or tracked_lane,
            "plan_reply": advance["reply"],
            "execution_reply": advance["execution_reply"],
            "parent_summary": advance["parent_summary"],
            "agent_reply": executed_reply,
            "queue_result": queue_result,
            "reply": None,
        }
    finally:
        release_top_level_task(channel["id"], thread_ts, processed=processed_successfully)


def cmd_channels(user_token: str) -> None:
    rows = list_channels(user_token)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_summary(user_token: str, ident: str, limit: int) -> None:
    channel = resolve_channel(user_token, ident)
    names = user_name_map(user_token)
    messages = channel_history(user_token, channel["id"], limit=limit)
    print(summarize_messages(channel, messages, names))


def cmd_post(user_token: str, ident: str, text: str) -> None:
    channel = resolve_channel(user_token, ident)
    print(json.dumps(post_message(channel["id"], text), ensure_ascii=False, indent=2))


def cmd_reply(user_token: str, ident: str, thread_ts: str, text: str) -> None:
    channel = resolve_channel(user_token, ident)
    print(json.dumps(reply_thread(channel["id"], thread_ts, text), ensure_ascii=False, indent=2))


def cmd_set_default(user_token: str, ident: str) -> None:
    channel = resolve_channel(user_token, ident)
    state = load_state()
    state["default_channel"] = channel["name"]
    state["default_channel_id"] = channel["id"]
    save_state(state)
    print(json.dumps({
        "ok": True,
        "default_channel": channel["name"],
        "default_channel_id": channel["id"],
        "message": f"已將 #{channel['name']} 設為預設控盤頻道",
    }, ensure_ascii=False, indent=2))


def cmd_show_default(user_token: str) -> None:
    channel = get_default_channel(user_token)
    print(json.dumps(channel, ensure_ascii=False, indent=2))


def cmd_control_status(user_token: str, limit: int) -> None:
    channel = get_default_channel(user_token)
    names = user_name_map(user_token)
    messages = channel_history(user_token, channel["id"], limit=limit)
    print(build_control_status(channel, messages, names))


def cmd_default_post(user_token: str, text: str) -> None:
    channel = get_default_channel(user_token)
    print(json.dumps(post_message(channel["id"], text), ensure_ascii=False, indent=2))


def cmd_default_reply(user_token: str, thread_ts: str, text: str) -> None:
    channel = get_default_channel(user_token)
    print(json.dumps(reply_thread(channel["id"], thread_ts, text), ensure_ascii=False, indent=2))


def cmd_watch_once(user_token: str) -> None:
    channel = get_default_channel(user_token)
    print(json.dumps(watch_once(user_token, channel), ensure_ascii=False, indent=2))


def cmd_watch_loop(user_token: str, interval: float) -> None:
    channel = get_default_channel(user_token)
    ensure_singleton_watcher(channel["name"])
    print(f"watch-loop started for #{channel['name']} (interval={interval}s)", flush=True)
    try:
        while True:
            try:
                result = watch_once(user_token, channel)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            except Exception as exc:
                print(json.dumps({"ok": False, "action": "error", "error": str(exc)}, ensure_ascii=False), flush=True)
            time.sleep(interval)
    finally:
        clear_singleton_watcher()


def cmd_lanes(user_token: str) -> None:
    channel = get_default_channel(user_token)
    rows = list_lanes(channel["id"])
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_lane_status(lane_id: str) -> None:
    lane = get_lane(lane_id)
    if not lane:
        raise SystemExit(f"Lane not found: {lane_id}")
    print(json.dumps(lane, ensure_ascii=False, indent=2))


def cmd_execute_lane(lane_id: str) -> None:
    print(json.dumps(execute_lane(lane_id), ensure_ascii=False, indent=2))


def cmd_transition_lane(lane_id: str, status: str, note: str | None = None) -> None:
    print(json.dumps(transition_lane(lane_id, status=status, note=note), ensure_ascii=False, indent=2))


def cmd_queue_status() -> None:
    print(json.dumps(queue_status(), ensure_ascii=False, indent=2))


def cmd_run_queue_once() -> None:
    print(json.dumps(run_queue_once(), ensure_ascii=False, indent=2))


def cmd_watcher_status() -> None:
    print(json.dumps(watcher_status(), ensure_ascii=False, indent=2))


def cmd_ensure_watcher(user_token: str) -> None:
    channel = get_default_channel(user_token)
    print(json.dumps(ensure_watcher_running(channel["name"]), ensure_ascii=False, indent=2))


def cmd_cleanup_stale_watchers() -> None:
    print(json.dumps(cleanup_stale_watchers(), ensure_ascii=False, indent=2))


def cmd_reconcile_stale_lanes(max_age_seconds: int) -> None:
    print(json.dumps(reconcile_stale_lanes(max_age_seconds=max_age_seconds), ensure_ascii=False, indent=2))


def main() -> None:
    bot_token, user_token = load_env()
    parser = argparse.ArgumentParser(description="Slack MCP 老闆模式控盤工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("channels", help="列出可讀取的公開頻道")

    p_set_default = sub.add_parser("set-default", help="設定預設控盤頻道")
    p_set_default.add_argument("channel")

    sub.add_parser("show-default", help="顯示目前預設控盤頻道")

    p_control_status = sub.add_parser("control-status", help="輸出預設控盤頻道的老闆模式快照")
    p_control_status.add_argument("--limit", type=int, default=12)

    p_summary = sub.add_parser("summary", help="輸出指定頻道最近訊息的老闆模式摘要")
    p_summary.add_argument("channel")
    p_summary.add_argument("--limit", type=int, default=12)

    p_post = sub.add_parser("post", help="透過 Slack MCP 主動發訊息")
    p_post.add_argument("channel")
    p_post.add_argument("text")

    p_default_post = sub.add_parser("default-post", help="對預設控盤頻道主動發訊息")
    p_default_post.add_argument("text")

    p_reply = sub.add_parser("reply", help="透過 Slack MCP 回覆指定 thread")
    p_reply.add_argument("channel")
    p_reply.add_argument("thread_ts")
    p_reply.add_argument("text")

    p_default_reply = sub.add_parser("default-reply", help="回覆預設控盤頻道的指定 thread")
    p_default_reply.add_argument("thread_ts")
    p_default_reply.add_argument("text")

    sub.add_parser("watch-once", help="掃描預設控盤頻道，遇到新的 top-level 交辦就自動開 thread kickoff")

    p_watch_loop = sub.add_parser("watch-loop", help="持續輪詢預設控盤頻道並自動開 thread kickoff")
    p_watch_loop.add_argument("--interval", type=float, default=10.0)

    sub.add_parser("lanes", help="列出預設控盤頻道目前已建立的 lane")

    p_lane_status = sub.add_parser("lane-status", help="查看單一 lane 狀態")
    p_lane_status.add_argument("lane_id")

    p_execute_lane = sub.add_parser("execute-lane", help="對單一 lane 啟動第一版子代理執行")
    p_execute_lane.add_argument("lane_id")

    p_block_lane = sub.add_parser("block-lane", help="把 lane 標成 blocked 並回覆 thread")
    p_block_lane.add_argument("lane_id")
    p_block_lane.add_argument("--note", default="")

    p_complete_lane = sub.add_parser("complete-lane", help="把 lane 標成 completed 並回覆 thread")
    p_complete_lane.add_argument("lane_id")
    p_complete_lane.add_argument("--note", default="")

    p_close_lane = sub.add_parser("close-lane", help="把 lane 標成 closed 並回覆 thread")
    p_close_lane.add_argument("lane_id")
    p_close_lane.add_argument("--note", default="")

    sub.add_parser("queue-status", help="查看目前 lane execution queue 狀態")
    sub.add_parser("run-queue-once", help="手動執行一次 lane queue worker")

    sub.add_parser("watcher-status", help="查看目前 watch-loop 單例值班狀態")
    sub.add_parser("ensure-watcher", help="確認是否已有 watch-loop 在值班")
    sub.add_parser("cleanup-stale-watchers", help="清掉未被 state 追蹤的舊 watch-loop 進程")
    p_reconcile_stale = sub.add_parser("reconcile-stale-lanes", help="把長時間未更新的非終態 lane 標成 stale")
    p_reconcile_stale.add_argument("--max-age-seconds", type=int, default=1800)

    args = parser.parse_args()

    if args.cmd == "channels":
        cmd_channels(user_token)
    elif args.cmd == "set-default":
        cmd_set_default(user_token, args.channel)
    elif args.cmd == "show-default":
        cmd_show_default(user_token)
    elif args.cmd == "control-status":
        cmd_control_status(user_token, args.limit)
    elif args.cmd == "summary":
        cmd_summary(user_token, args.channel, args.limit)
    elif args.cmd == "post":
        cmd_post(user_token, args.channel, args.text)
    elif args.cmd == "default-post":
        cmd_default_post(user_token, args.text)
    elif args.cmd == "reply":
        cmd_reply(user_token, args.channel, args.thread_ts, args.text)
    elif args.cmd == "default-reply":
        cmd_default_reply(user_token, args.thread_ts, args.text)
    elif args.cmd == "watch-once":
        cmd_watch_once(user_token)
    elif args.cmd == "watch-loop":
        cmd_watch_loop(user_token, args.interval)
    elif args.cmd == "lanes":
        cmd_lanes(user_token)
    elif args.cmd == "lane-status":
        cmd_lane_status(args.lane_id)
    elif args.cmd == "execute-lane":
        cmd_execute_lane(args.lane_id)
    elif args.cmd == "block-lane":
        cmd_transition_lane(args.lane_id, "blocked", args.note)
    elif args.cmd == "complete-lane":
        cmd_transition_lane(args.lane_id, "completed", args.note)
    elif args.cmd == "close-lane":
        cmd_transition_lane(args.lane_id, "closed", args.note)
    elif args.cmd == "queue-status":
        cmd_queue_status()
    elif args.cmd == "run-queue-once":
        cmd_run_queue_once()
    elif args.cmd == "watcher-status":
        cmd_watcher_status()
    elif args.cmd == "ensure-watcher":
        cmd_ensure_watcher(user_token)
    elif args.cmd == "cleanup-stale-watchers":
        cmd_cleanup_stale_watchers()
    elif args.cmd == "reconcile-stale-lanes":
        cmd_reconcile_stale_lanes(args.max_age_seconds)


if __name__ == "__main__":
    main()
